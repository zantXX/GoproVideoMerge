import os
from dotenv import load_dotenv
from pathlib import Path
from src.fileListing import video_key_listing
from src.ffmpeg import write_file_list, video_concat, delete_file_list

load_dotenv(".env",override=True)

# 動画ファイルの参照元
raw_video_root = os.getenv("RAW_VIDEO_DIR")
# ffmpegの指示書のパス
temp_ffmpeg_dir = os.getenv("TEMP_FFMPEG_DIR")
# 動画ファイルの保存場所
dst_video_root = os.getenv("CONCAT_VIDEO_DIR")
# ffmpegの指示書の自動削除
delete_ffmpeg_file = os.getenv("TEMP_FFMPEG_DELETE", "False").upper() == "TRUE"

# 動画ファイル洗い出し
video_set = video_key_listing(Path(raw_video_root))

# 動画の識別番号ごとにffmpegのテキストファイル化
write_file_list(video_set, Path(temp_ffmpeg_dir))

# 動画結合
for ffmpeg_file in Path(temp_ffmpeg_dir).glob("*.txt"):
    path = Path(ffmpeg_file)
    video_concat(path, Path(dst_video_root), f"GX{path.stem}")

# ffmpegのテキストファイルを削除
if delete_ffmpeg_file:
    delete_file_list(Path(temp_ffmpeg_dir))



