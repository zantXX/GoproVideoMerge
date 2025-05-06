# GoPro動画結合ツール

このリポジトリは、GoProで撮影した複数の動画ファイルを簡単に結合するためのPythonスクリプトです。  
元リポジトリ: [CUQS/ConcatenateYourGoproVideo](https://github.com/CUQS/ConcatenateYourGoproVideo) をベースに編集しています。

## 必要条件

- [ffmpeg](https://ffmpeg.org/) がインストールされていること
- [uv](https://github.com/astral-sh/uv)（高速なPythonパッケージマネージャ）

## 使い方

1. `.env` ファイルを編集し、各ディレクトリパスを自分の環境に合わせて設定してください。PathlibによってwindowsPathでもLinuxPathでも動きます。

例:
```properties
RAW_VIDEO_DIR="C:\ubuntu_share\gopro\2025-05-06"
CONCAT_VIDEO_DIR="C:\ubuntu_share\gopro\2025-05-06"
TEMP_FFMPEG_DIR="./tmp_ffmpeg"
TEMP_FFMPEG_DELETE=TRUE
```

2. スクリプトを実行します。

```bash
uv run gopro_concat.py
```

## オプション

- `.env` の `TEMP_FFMPEG_DELETE` を `TRUE` にすると、結合後に一時ファイル（ffmpeg用テキストファイル）が自動で削除されます。

## 注意事項

- `ffmpeg` のパスが通っていない場合は、環境変数に追加してください。
- 元動画ファイルはGoProHero8の標準的なファイル構成を想定しています。