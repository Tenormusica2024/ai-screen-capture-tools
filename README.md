# AI Screen Capture Tools

AIエージェントのための画面キャプチャツール群。ターミナル上のAIエージェントが自律的に画面確認できるよう設計されたシンプルなPythonスクリプト集です。

## 背景

ターミナル上のAIエージェントに「今この画面を見てほしい」という場面は意外と多くあります。

- UIを軽く直したあとのレイアウト確認
- DevToolsにだけ出ているエラーの共有
- 一時的なダイアログや設定画面のスクリーンショット

こういう「ちょっと画面を見てコメントしてほしい」系の相談は、テキストだけではどうしても伝わりづらい一方で、毎回手動でスクショを撮ってファイルを探して……というのもけっこう面倒です。

このツール群を使うと、AIエージェントがシステムプロンプトを読むだけで、自律的に画面キャプチャ→確認→クリーンアップまで実行できるようになります。

## ツール構成

- **screen_capture_full.py**: 画面キャプチャのメイン。モニターを自動認識して、必要な領域をPNGとして保存
- **image_quadrant_crop.py**: 既存のPNGを4分割。AIが「もう一段階だけズーム」して見たいときに使う補助ツール
- **cleanup_snips.py**: 溜まりがちなスクリーンショットを一括削除するクリーンアップ用スクリプト

## インストール

### 必要な環境

- Windows (Windows API を使用)
- Python 3.6+
- Pillow

### セットアップ

```bash
pip install -r requirements.txt
```

## 使用方法

### screen_capture_full.py

#### 全モニターを4分割してキャプチャ

```bash
python screen_capture_full.py
```

出力例:
- `screen_20251201_143025_main_tl.png` (メインモニター左上)
- `screen_20251201_143025_main_tr.png` (メインモニター右上)
- `screen_20251201_143025_main_bl.png` (メインモニター左下)
- `screen_20251201_143025_main_br.png` (メインモニター右下)
- `screen_20251201_143025_sub1_tl.png` (サブモニター1左上)
- ...

#### 特定のモニター・領域のみキャプチャ

```bash
# メインモニターの左下だけ
python screen_capture_full.py main bl

# サブモニター1の右上だけ
python screen_capture_full.py sub1 tr
```

領域指定:
- `tl`: 左上 (top-left)
- `tr`: 右上 (top-right)
- `bl`: 左下 (bottom-left)
- `br`: 右下 (bottom-right)

#### モニター全体をキャプチャ（分割なし）

```bash
# 全モニターを1枚の画像として保存
python screen_capture_full.py --single

# モニターごとに1枚ずつ保存
python screen_capture_full.py --split
```

### image_quadrant_crop.py

既存の画像をさらに4分割します。

```bash
# 4分割してから元画像を削除
python image_quadrant_crop.py "path/to/screen_20251201_143025.png" --cleanup

# 4分割のみ（元画像は残す）
python image_quadrant_crop.py "path/to/screen_20251201_143025.png"
```

### cleanup_snips.py

```bash
# すべてのPNG/JPGを削除
python cleanup_snips.py --all

# 60分以上古いファイルのみ削除（デフォルト）
python cleanup_snips.py
```

## 環境変数

### SCREENSHOT_SAVE_DIR

スクリーンショットの保存先ディレクトリを変更できます。

```bash
# Windows
set SCREENSHOT_SAVE_DIR=C:\Users\YourName\Screenshots
python screen_capture_full.py

# PowerShell
$env:SCREENSHOT_SAVE_DIR="C:\Users\YourName\Screenshots"
python screen_capture_full.py
```

デフォルト: `<SCRIPT_DIR>/../snips`

## AIエージェントからの使用

このツール群の最大のポイントは、**人間が細かい操作を覚えなくても、システムプロンプトさえ読んでいればAIエージェント側が自律的に使える**ことです。

例えば、ユーザーが「サブモニターの左上を見て」と指示すると:

1. AIエージェントがシステムプロンプトを確認
2. 適切な `screen_capture_full.py` コマンドを組み立て
3. スクショを取得して内容を確認
4. 必要なら `image_quadrant_crop.py` でズーム
5. 用が済んだら `cleanup_snips.py` で整理

この一連の流れが、人間の介入なしで自動的に実行されます。

## DPIスケーリングとマルチモニター

- **メインモニター**: `ImageGrab.grab()` から直接4分割するため、125% / 150% などのスケーリングでも問題なし
- **サブモニター**: Windows の仮想スクリーン座標を使用。一般的な「ノートPC＋外付け1枚」構成では実用上問題ありません

モニターごとに極端なDPI設定が混在する特殊な環境では、数ピクセル単位のずれが出る可能性がありますが、UIレビュー用途なら許容範囲です。

## ライセンス

MIT License
