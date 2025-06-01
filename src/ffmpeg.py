import subprocess
from time import sleep
from pathlib import Path
from typing import Tuple
import sys # For platform check

# Definition of write_file_list (assuming it's already in the file)
def write_file_list(video_set:dict, temp_ffmpeg_dir:Path) -> None:
    # フォルダかどうかを判別
    if not temp_ffmpeg_dir.is_dir():
        temp_ffmpeg_dir.mkdir(parents=True, exist_ok=True) # Create if not exists
    
    # 動画の識別番号ごとにリスト化
    for key in video_set.keys():
        # 動画の識別番号ごとにファイルを作成
        with open(temp_ffmpeg_dir.joinpath(key+".txt"), "w") as f:
            # ffconcat形式で書き込む時のおまじない
            f.write("ffconcat version 1.0\n")
            # 結合するファイルを書き込む
            for path_str in video_set[key]: # Assuming video_set[key] contains string paths
                f.write(f"file '{Path(path_str).resolve()}'\n")


# Definition of delete_file_list (assuming it's already in the file)
def delete_file_list(temp_ffmpeg_dir:Path) -> None:
    if not temp_ffmpeg_dir.is_dir():
        print(f"Info: Directory {temp_ffmpeg_dir} not found for deletion of .txt files.")
        return

    deleted_count = 0
    for file_path in temp_ffmpeg_dir.glob("*.txt"):
        try:
            file_path.unlink()
            print(f"delete {file_path.name}")
            deleted_count +=1
        except Exception as e:
            print(f"Error deleting file {file_path.name}: {e}")
    if deleted_count == 0:
        print(f"No .txt files found to delete in {temp_ffmpeg_dir}.")


def video_concat(video_list:Path, dist_video_root:Path, video_output_name:str, override:bool = True, sleep_time:int =1) -> Tuple[str, str, int]:
    '''
    Concatenates videos using ffmpeg and captures its output.

    Args:
        video_list: Path to the ffmpeg input file list (text file).
        dist_video_root: Path to the directory where the output video will be saved.
        video_output_name: Name of the output video file (without extension).
        override: Whether to overwrite the output file if it exists.
        sleep_time: Time to sleep after the subprocess call.

    Returns:
        A tuple containing (stdout, stderr, return_code) from the ffmpeg process.
    '''
    listing_file = str(video_list.resolve())
    output_file = dist_video_root.joinpath(f"{video_output_name}.mp4")
    output_path = str(output_file.resolve())

    override_arg = "-y" if override else "-n"
    
    command = [
        "ffmpeg", override_arg,
        "-f", "concat",
        "-safe", "0",
        "-i", listing_file,
        "-c", "copy",
        output_path
    ]
    
    try:
        dist_video_root.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return "", f"出力先ディレクトリの作成に失敗しました: {output_file.parent} ({e})", -3

    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NO_WINDOW

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            errors='replace',
            creationflags=creation_flags
        )

        if sleep_time > 0:
            sleep(sleep_time)

        return process.stdout, process.stderr, process.returncode

    except FileNotFoundError:
        return "", "ffmpegコマンドが見つかりません。インストールされているか、PATHを確認してください。", -1
    except Exception as e:
        return "", f"ffmpegの実行中に予期せぬエラーが発生しました: {e}", -2

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    from .fileListing import video_key_listing

    print("--- ffmpeg.py script execution for testing ---")
    dotenv_path = Path(__file__).resolve().parent.parent.joinpath('.env')
    load_dotenv(dotenv_path=dotenv_path, override=True)
    
    raw_video_root_env = os.getenv("RAW_VIDEO_DIR")
    temp_ffmpeg_dir_env = os.getenv("TEMP_FFMPEG_DIR", str(Path(__file__).resolve().parent.joinpath("tmp_ffmpeg_test")))
    dst_video_root_env = os.getenv("CONCAT_VIDEO_DIR")

    if not raw_video_root_env or not dst_video_root_env:
        print(f"環境変数が正しく設定されていません。プロジェクトルートの .env ファイルに RAW_VIDEO_DIR, CONCAT_VIDEO_DIR を設定してください。")
        print(f"現在の設定値: RAW_VIDEO_DIR='{raw_video_root_env}', CONCAT_VIDEO_DIR='{dst_video_root_env}', TEMP_FFMPEG_DIR='{temp_ffmpeg_dir_env}'")
    else:
        raw_video_path = Path(raw_video_root_env)
        temp_ffmpeg_path = Path(temp_ffmpeg_dir_env)
        dst_video_path = Path(dst_video_root_env)

        temp_ffmpeg_path.mkdir(parents=True, exist_ok=True)
        dst_video_path.mkdir(parents=True, exist_ok=True)

        print(f"使用するパス:")
        print(f"  動画元フォルダ: {raw_video_path.resolve() if raw_video_path.exists() else raw_video_path} {'(存在しません)' if not raw_video_path.exists() else ''}")
        print(f"  一時ffmpeg指示書フォルダ: {temp_ffmpeg_path.resolve()}")
        print(f"  出力先フォルダ: {dst_video_path.resolve()}")

        print("\n--- video_key_listing のテスト ---")
        video_set = {}
        if not raw_video_path.exists():
            print(f"エラー: 動画元フォルダ {raw_video_path} が存在しません。テストを続行できません。")
        else:
            try:
                video_set = video_key_listing(raw_video_path)
                print(f"検出された動画セット: {list(video_set.keys()) if video_set else '(なし)'}")
            except ValueError as e:
                print(f"エラー: {e}")
            except Exception as e:
                print(f"video_key_listing 中に予期せぬエラー: {e}")

        if video_set:
            print("\n--- write_file_list のテスト ---")
            try:
                write_file_list(video_set, temp_ffmpeg_path)
                print(f"{temp_ffmpeg_path.resolve()} の内容:")
                found_txt = False
                for file_item in temp_ffmpeg_path.glob("*.txt"):
                    print(f"  - {file_item.name}")
                    found_txt = True
                if not found_txt: print("  ( .txt ファイルが見つかりません)")
            except Exception as e:
                print(f"write_file_list 中に予期せぬエラー: {e}")

            test_ffmpeg_file_path = None
            if video_set :
                first_key = list(video_set.keys())[0]
                test_ffmpeg_file_path = temp_ffmpeg_path.joinpath(f"{first_key}.txt")

            if test_ffmpeg_file_path and test_ffmpeg_file_path.exists():
                print(f"\n--- video_concat のテスト (対象: {test_ffmpeg_file_path.name}) ---")
                test_output_name = f"GX{test_ffmpeg_file_path.stem}_ffmpeg_py_test"

                stdout, stderr, retcode = video_concat(test_ffmpeg_file_path, dst_video_path, test_output_name, override=True)

                stdout_str = stdout if isinstance(stdout, str) else ""
                stderr_str = stderr if isinstance(stderr, str) else ""

                print(f"  ffmpeg stdout:\n{stdout_str if stdout_str.strip() else '(なし)'}")
                print(f"  ffmpeg stderr:\n{stderr_str if stderr_str.strip() else '(なし)'}")
                print(f"  ffmpeg return code: {retcode}")

                if retcode == 0:
                    print(f"  動画結合成功: {dst_video_path.joinpath(test_output_name + '.mp4')}")
                elif retcode == -1:
                    print("  動画結合失敗: ffmpegコマンドが見つかりません。")
                elif retcode == -2:
                     print("  動画結合失敗: ffmpeg実行中に予期せぬエラー。")
                elif retcode == -3:
                     print("  動画結合失敗: 出力ディレクトリ作成エラー。")
                else:
                    print(f"  動画結合失敗: ffmpegエラー (リターンコード: {retcode})。stderrを確認してください。")
            elif not video_set:
                print(f"動画セットが空のため video_concat のテストはスキップします。")
            else:
                print(f"テスト用のffmpeg指示ファイル ({test_ffmpeg_file_path}) が見つかりません。write_file_listが正しく動作したか確認してください。")
        else:
            print("\n動画セットが見つからなかったため、ffmpeg関連のテスト (write_file_list, video_concat) はスキップします。")

    print("\n--- ffmpeg.py script execution finished ---")
