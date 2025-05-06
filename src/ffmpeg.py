import subprocess
from time import sleep
from pathlib import Path
"""
ffmpegの基礎
-f concat: concat形式であることを指定。ffmpeg -formatsで確認可能。本来なら、コーデックなどを指定。
-safe 0: safe modeを指定。相対パスのファイルは読み込まない
-i videolist.txt: 入力ファイルを指定。動画ファイルのリストを指定することも可能
-c copy: コーデックを指定。つなげる動画が同じコーディックであれば、copyで高速に動作可能
-y : 上書きすることを指定。上書きしない場合は、-nを指定する

ffmpegのconcat形式については、以下を参照
https://trac.ffmpeg.org/wiki/Concatenate
https://ffmpeg.org/ffmpeg-formats.html#concat
"""

def write_file_list(video_set:dict, temp_ffmpeg_dir:Path) -> None:
    # フォルダかどうかを判別
    if not temp_ffmpeg_dir.is_dir():
        raise ValueError(f"{temp_ffmpeg_dir} is not a directory.")
    
    # 動画の識別番号ごとにリスト化
    for key in video_set.keys():
        # 動画の識別番号ごとにファイルを作成
        with open(temp_ffmpeg_dir.joinpath(key+".txt"), "w") as f:
            # ffconcat形式で書き込む時のおまじない
            f.write("ffconcat version 1.0\n")
            # 結合するファイルを書き込む
            for path in video_set[key]:
                f.write(f"file '{path}'\n")


def video_concat(video_list:Path, dist_video_root:Path, video_output_name:str, override:bool = True,sleep_time:int =1) -> None:
    listing_file = str(video_list.absolute())
    output_path = str(dist_video_root.absolute()) + "/" + video_output_name + ".mp4"
    override = "-y" if override else "-n"
    subprocess.run(["ffmpeg", override, "-f", "concat", "-safe", "0", "-i", listing_file, "-c", "copy", output_path])
    sleep(sleep_time)

def delete_file_list(temp_ffmpeg_dir:Path) -> None:
    # フォルダかどうかを判別
    if not temp_ffmpeg_dir.is_dir():
        raise ValueError(f"{temp_ffmpeg_dir} is not a directory.")
    
    # temp_ffmpeg_dirのフォルダに含まれる.txtファイルを全て削除する
    for file in temp_ffmpeg_dir.glob("*.txt"):
        print(f"delete {file.name}")
        file.unlink()
    

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    from fileListing import video_key_listing
    # 環境変数の読み込み
    load_dotenv("../.env",override=True)
    # 入力ファイルの指定
    ## 動画ファイルの参照元
    raw_video_root = os.getenv("RAW_VIDEO_DIR")
    print(f"raw_video_root: {raw_video_root}")
    ## ffmpegの指示書のパス
    temp_ffmpeg_dir = os.getenv("TEMP_FFMPEG_DIR")
    print(f"temp_ffmpeg_dir: {temp_ffmpeg_dir}")
    ## 動画ファイルの保存場所
    dst_video_root = os.getenv("CONCAT_VIDEO_DIR")
    print(f"dst_video_root: {dst_video_root}")

    # 動画ファイル洗い出しのテスト
    video_set = video_key_listing(Path(raw_video_root))
    print(f"video_set: {video_set}")

    # 動画の識別番号ごとにffmpegのテキストファイル化するテスト
    write_file_list(video_set, Path(temp_ffmpeg_dir))
    # temp_ffmpeg_dirのフォルダの中身を一行ずつ表示する
    print("temp_ffmpeg_dirのフォルダの中身")
    for file in Path(temp_ffmpeg_dir).glob("*.txt"):
        print(file.name)
    
    # 動画結合できるかテスト
    video_concat(Path("../tmp_ffmpeg/0689.txt"),Path(dst_video_root), "GX0689")
    print("動画結合完了")

    # ffmpegのテキストファイルを削除するテスト
    delete_file_list(Path(temp_ffmpeg_dir))
    print("削除完了")