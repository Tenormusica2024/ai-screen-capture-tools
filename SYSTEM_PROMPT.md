# システムプロンプト: AI Screen Capture Tools

このドキュメントは、AIエージェントが `ai-screen-capture-tools` を自律的に使用するためのガイドラインです。CLAUDE.md や agents.md に記載することを想定しています。

## 📸 Screen Capture Protocol

**UI確認・エラー確認時はAI Screen Capture Toolsを自律的に使用**

### 実行前提

- **環境変数 `PROJECT_ROOT` が設定済み**（推奨）
- スクリプト配置: `%PROJECT_ROOT%\Codex\tools`
- 保存先: `%PROJECT_ROOT%\Codex\snips`

### 環境変数設定

```bash
# Windows
set PROJECT_ROOT=C:\Users\YourName\MyProject

# PowerShell
$env:PROJECT_ROOT="C:\Users\YourName\MyProject"
```

環境変数が設定されていない場合、スクリプトの親ディレクトリの `snips` フォルダに保存されます。

---

## ツール説明

### screen_capture_full.py

**目的**: メインモニター（`main`）とサブモニター（`sub1` 以降）を自動認識し、AIエージェントが自律的に画面状態を確認できるようにする。

#### デフォルト実行

```bash
cd "%PROJECT_ROOT%\Codex\tools"
python screen_capture_full.py
```

**動作**: 各モニターを「左上 / 右上 / 左下 / 右下」に4分割した PNG を `%PROJECT_ROOT%\Codex\snips` 配下に保存する。

**出力例**:
- `screen_20251201_143025_main_tl.png` (メインモニター左上)
- `screen_20251201_143025_main_tr.png` (メインモニター右上)
- `screen_20251201_143025_main_bl.png` (メインモニター左下)
- `screen_20251201_143025_main_br.png` (メインモニター右下)
- `screen_20251201_143025_sub1_tl.png` (サブモニター1左上)
- ...

#### オプション実行

```bash
# 全モニターを1枚に保存
python screen_capture_full.py --single

# モニターごとに1枚ずつ保存
python screen_capture_full.py --split

# 特定モニター・領域のみキャプチャ
python screen_capture_full.py main bl  # メインモニター左下
python screen_capture_full.py sub1 tr  # サブモニター1右上
```

**領域指定**:
- `tl`: 左上 (top-left)
- `tr`: 右上 (top-right)
- `bl`: 左下 (bottom-left)
- `br`: 右下 (bottom-right)

---

### image_quadrant_crop.py

**目的**: 既存の PNG を 4 分割し、AIエージェントが「もう一段階だけズーム」して確認できるようにする。

#### 実行例

```bash
cd "%PROJECT_ROOT%\Codex\tools"
python image_quadrant_crop.py "%PROJECT_ROOT%\Codex\snips\screen_20251201_143025_main_tl.png" --cleanup
```

**動作**:
- 引数の PNG を「左上 / 右上 / 左下 / 右下」に4分割
- `*_tl.png`, `*_tr.png`, `*_bl.png`, `*_br.png` を同じフォルダに保存
- `--cleanup` を付けた場合、元の PNG は分割後に削除（生成した4枚は残す）

---

### cleanup_snips.py

**目的**: 溜まりがちなスクリーンショットを一括削除する。

#### 実行例

```bash
cd "%PROJECT_ROOT%\Codex\tools"

# 60分以上古いファイルのみ削除（デフォルト・推奨）
python cleanup_snips.py

# 全削除（⚠️ 注意: 必要なスクショも削除される）
python cleanup_snips.py --all --force
```

**⚠️ 重要**: `--all` フラグは全てのスクショを削除します。AIエージェントが自律的に実行する場合は、デフォルトの時間指定削除のみを使用してください。

---

## 運用ルール

### 自動発火条件（AIが自発的にスクショを撮る場合）

以下の場合、ユーザーからの明示的な依頼がなくても、必要に応じて自発的に `screen_capture_full.py` を実行してよい:

1. **UI修正をデプロイした直後**: レイアウト・スタイル変更後の確認
2. **ユーザーが「画面を見て」「スクショを撮って」と指示した時**
3. **DevToolsエラーの確認が必要な時**: コンソールエラーの視覚的確認
4. **レイアウト崩れの報告があった時**: UI状態の記録
5. **一時的なダイアログ・設定画面の説明時**: 「この状態になっていればOK」というUI状態の記録

**ただし、スクショ取得は最小限にとどめる**（不要なキャプチャは避ける）。

### 基本実行フロー

```bash
# 1. 全モニターを4分割キャプチャ
cd "%PROJECT_ROOT%\Codex\tools"
python screen_capture_full.py

# 2. Read ツールで画像内容を確認
Read(file_path="C:\\Users\\Tenormusica\\<PROJECT_NAME>\\Codex\\snips\\screen_*.png")

# 3. 必要なら特定領域を再キャプチャ
python screen_capture_full.py main tl  # メインモニター左上

# 4. さらにズームが必要な場合（1段階のみ）
python image_quadrant_crop.py "C:\\...\\screen_20251201_143025_main_tl.png" --cleanup

# 5. Read ツールで分割画像を確認
Read(file_path="C:\\Users\\Tenormusica\\<PROJECT_NAME>\\Codex\\snips\\screen_20251201_143025_main_tl_*.png")

# 6. 確認完了後にクリーンアップ（60分以上古いファイルのみ）
python cleanup_snips.py
```

### 読みやすさの確認

- VS Code や Obsidian の画面内容を確認したいときは、まずこのスクリプトで画面を取得し、その PNG を Read ツールで確認する
- 細かいUIテキストを読む必要がある場合は、必要なモニターと領域（例: `sub1 tl`）を指定して再キャプチャしてから回答する
- それでも読めない場合は、`image_quadrant_crop.py` で1段階だけズームして確認
- 16分の1相当の画像でも読めない場合は、それ以上のズーム（再分割）は行わず、**「この解像度では判読困難」と明示して回答する**

### ズーム制限

- **ズーム（分割）は 1 段階まで**
- 最初の4分割で読めない → `image_quadrant_crop.py` で再分割（16分の1相当）
- 16分の1でも読めない → 「現状の解像度では判読困難」として扱う

---

## 絶対禁止事項

1. ❌ **`cleanup_snips.py --all` の単独実行**
   - 必要なスクショも削除されるため、`--force` フラグなしでの実行は禁止
   - デフォルトの時間指定削除（60分以上古いファイル）のみ使用

2. ❌ **2段階以上のズーム**
   - 16分の1で判読困難なものは「判読困難」として報告
   - それ以上の分割は行わない

3. ❌ **snips ディレクトリ外の画像の分割**
   - `image_quadrant_crop.py` は `snips` 内の画像のみを対象とする
   - それ以外のディレクトリの画像は分割しない

---

## トラブルシューティング

### エラー: "Invalid SCREENSHOT_SAVE_DIR: parent directory does not exist"

**原因**: 環境変数 `SCREENSHOT_SAVE_DIR` で指定したディレクトリの親ディレクトリが存在しない

**解決策**:
1. 環境変数を削除するか、正しいパスを設定
2. または `PROJECT_ROOT` を設定して、デフォルトの保存先を使用

### エラー: "This script requires Windows OS"

**原因**: Windows以外のOSで実行された

**解決策**: このツールはWindows専用です。macOSやLinuxでは使用できません。

### ファイルが保存されない

**原因**: 保存先ディレクトリが存在しないか、書き込み権限がない

**確認手順**:
1. `PROJECT_ROOT` 環境変数が正しく設定されているか確認
2. `%PROJECT_ROOT%\Codex\snips` ディレクトリの存在と書き込み権限を確認

---

## まとめ

- AIエージェントは、UI確認・エラー確認時に自律的にこのツールを使用できる
- `PROJECT_ROOT` 環境変数を設定することで、保存先を統一できる
- ズームは1段階まで、cleanup は時間指定削除のみを使用
- システムプロンプトを読むだけで、AIが適切にツールを使い分けられる
