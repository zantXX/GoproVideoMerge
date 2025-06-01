# GoPro動画結合ツール

このリポジトリは、GoProで撮影した複数の動画ファイルを簡単に結合するためのツールです。
コマンドラインスクリプトとGUIアプリケーションの両方を提供します。
元リポジトリ: [CUQS/ConcatenateYourGoproVideo](https://github.com/CUQS/ConcatenateYourGoproVideo) をベースに編集しています。

## 必要条件

- [ffmpeg](https://ffmpeg.org/) がインストールされ、システムのPATHに含まれていること。
- [uv](https://github.com/astral-sh/uv)（高速なPythonパッケージマネージャ）。
- Python 3.x

## セットアップ

1. リポジトリをクローンします:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Pythonの依存関係をインストールします:
   ```bash
   uv pip install -r requirements.txt
   ```
   または、`pyproject.toml` に記載の依存関係 (`python-dotenv`, `customtkinter`) を `uv pip install customtkinter python-dotenv` のように直接インストールします。
   (`requirements.txt` がない場合は、`uv run pip freeze > requirements.txt` で作成できますが、`pyproject.toml` があれば `uv pip install .` でも可)

## GUIアプリケーションの使い方

GUIアプリケーションを利用することで、より直感的に動画結合プロセスを実行できます。

1.  **GUIの起動:**
    ```bash
    uv run python gopro_gui.py
    ```

2.  **操作方法:**
    *   **Raw Video Folder:** 「Select Folder」ボタンをクリックし、結合したいGoPro動画ファイル (`GX*.MP4`) が含まれるフォルダを選択します。選択したパスがテキストフィールドに表示されます。
    *   **Output Folder:** 「Select Folder」ボタンをクリックし、結合された動画を保存するフォルダを選択します。選択したパスがテキストフィールドに表示されます。
    *   **Delete temporary ffmpeg files after concatenation:** このチェックボックスをオン（デフォルト）にすると、動画結合後に一時的に作成される `ffmpeg` 用の指示ファイル (`*.txt`) が `tmp_ffmpeg_gui` フォルダから削除されます。オフにすると、これらのファイルは残ります。
    *   **Start Concatenation:** 上記フォルダを選択後、このボタンをクリックすると動画結合プロセスが開始されます。処理中はボタンが無効化されます。
    *   **ログエリア:** GUI下部のテキストエリアには、処理の進捗状況、エラーメッセージ、完了通知などが表示されます。

3.  **一時ファイル:**
    *   GUIは、処理中に `ffmpeg` のための指示ファイルを `tmp_ffmpeg_gui` という名前のフォルダをリポジトリのルートディレクトリに作成（または使用）して保存します。

## コマンドラインスクリプトの使い方 (従来の方法)

1.  `.env` ファイルを編集し、各ディレクトリパスを自分の環境に合わせて設定してください。PathlibによってwindowsPathでもLinuxPathでも動きます。
    ルートディレクトリに `.env.example` をコピーして `.env` を作成し、編集してください。

    例:
    ```properties
    RAW_VIDEO_DIR="C:\ubuntu_share\gopro\2025-05-06" # Windowsパスの例
    CONCAT_VIDEO_DIR="/mnt/c/ubuntu_share/gopro/2025-05-06" # WSL/Linuxパスの例
    TEMP_FFMPEG_DIR="./tmp_ffmpeg"
    TEMP_FFMPEG_DELETE=TRUE
    ```

2.  スクリプトを実行します。
    ```bash
    uv run gopro_concat.py
    ```

## オプション (コマンドライン)

-   `.env` の `TEMP_FFMPEG_DELETE` を `TRUE` にすると、結合後に一時ファイル（ffmpeg用テキストファイル）が自動で削除されます。

## 注意事項

-   元動画ファイルはGoProHero8の標準的なファイル構成 (`GXddnnnn.MP4`) を想定しています。
-   `ffmpeg` が正しくインストールされ、PATHが通っていることを確認してください。通っていない場合、`video_concat` 関数内で `FileNotFoundError` が発生する可能性があります。

```
