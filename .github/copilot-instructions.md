# GoPro動画結合ツール github copilot向け指示書

このリポジトリは、GoProで撮影した複数の動画ファイルを簡単に結合するためのPythonスクリプトです。  
元リポジトリ: [CUQS/ConcatenateYourGoproVideo](https://github.com/CUQS/ConcatenateYourGoproVideo) をベースに編集しています。

## 指示

- pythonのコードを修正するときは、関数にgoogle doc styleのdoctringsを追加して、変数にはType Hintsをつけてください。
- コードの可読性を高めるために、必要に応じてコメントを追加してください。
- パスの操作には `pathlib` を使用してください。これにより、WindowsとLinuxの両方で動作するコードになります。
- 各種ハイパーパラメータは`.env`に記述し、`dotenv` パッケージを使用して読み込んでください。
- **これから、pythonスクリプトではなく、GUIで操作できるように画面を作成してください。**
    - 画面作成は、ステップバイステップで進めてください。
    - まずは、画面を構成するのに最適なライブラリの決定を行ってください。候補はいくつか提示し、windows, Linux両方で動作するものを選んでください。
    - つぎに画面に必要な要素を決定してください。ユーザが動画が存在するフォルダを選択できるようにすることと、ユーザがどこに結合した動画を保存するかは選択できるようにしてください。
    - その後、既存のコードをGUIに組み込む形で画面を実装してください。画面の要素はルートフォルダに配置する一つのファイルで完結させるようにしてください。
    - 画面を構成するコードを記述した後は、実際にGUIを起動して画面が正しく動作するかを確かめてください。必要に応じてターミナルや、スクリーンショットを使ってもかまいません(ツールが利用可能な場合)。
    - 全て画面が正常に動くことを確認したら、GUIの操作方法をREADMEに追記してください。
    - 最後にユーザにコードの確認を行って終了になります。



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