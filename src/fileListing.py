from pathlib import Path
""""
gopro hero8でのファイル名の付き方
例：GX010650.MP4

GX(0-1桁)：動画ファイル:type
01(2-3桁)：連番:num
0650(4-7桁)：動画群の識別番号:key
.MP4(8-11桁)：拡張子。サムネイルなら.THM。プロファイルなら.LRV(low resolution video)

よって、
①「GX」であり、「.MP4」であり、「同じ4桁の識別番号」でなるものを洗い出し、
②連番でつなげることが必要
"""
# フォルダの中のファイルを検索して、動画の識別番号ごとにリスト化する
def video_key_listing(raw_video_root:Path) -> dict:
    # フォルダかどうかを判別
    if not raw_video_root.is_dir():
        raise ValueError(f"{raw_video_root} is not a directory.")
    
    # フォルダ内の全てのファイルを取得
    mp4list = list(raw_video_root.glob("*.MP4"))

    # 動画の識別番号ごとにリスト化
    video_set = {}
    for file in mp4list:
        kind = file.name[0:2]
        num = file.name[2:4]
        key = file.name[4:8]
        if kind != "GX" or len(file.name) != 12:
            continue
        if key not in video_set:
            video_set[key] = []
        video_set[key].append(str(file.absolute()))
    # video_setのkeyに格納されているファイルパスのリストをソートする
    for key in video_set.keys():
        video_set[key].sort()
    return video_set

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    # 環境変数の読み込み
    load_dotenv("../.env",override=True)
    # 入力ファイルの指定
    ## 動画ファイルの参照元
    raw_video_root = os.getenv("RAW_VIDEO_DIR")
    print(f"raw_video_root: {raw_video_root}")
    ## ffmpegの指示書のパス
    temp_ffmpeg_dir = os.getenv("TEMP_FFMPEG_DIR")
    print(f"temp_ffmpeg_dir: {temp_ffmpeg_dir}")

    # 動画ファイル洗い出しのテスト
    video_set = video_key_listing(Path(raw_video_root))
    print(f"video_set: {video_set}")