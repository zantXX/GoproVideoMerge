import subprocess
from time import sleep
import os, sys

""""
gopro hero8でのファイル名の付き方
GX010650.MP4

GX(0-1桁)：動画ファイル。
01(2-3桁)：連番
0650(4-7桁)：動画群の識別番号
.MP4(8-11桁)：拡張子。サムネイルなら.THM。プロファイルなら.LRV(low resolution video)

よって、
①「GX」であり、「.MP4」であり、「同じ4桁の識別番号」でなるものを洗い出し、
②連番でつなげることが必要


VISION
①フォルダ内のすべての動画群を一括で、結合
②GUIで操作可能にする
"""

# 入力ファイルの指定
## 動画ファイルの参照元
raw_video_root = "/media/zant/6414EC4114EC17B6/ubuntu_share/gopro/2024-11-10/"
## 動画ファイルの保存場所
dst_video_root = "/media/zant/6414EC4114EC17B6/ubuntu_share/gopro/2024-11-10/"
## 対象となるビデオ群
video_idx = input("last 4 number of the video (xxxx-xxxx or xxxx): ").strip().replace("\n", "")
## 動画スピード
speed = 1.0
# 出力ファイル名
video_output_name = "GX" + video_idx


#入力チェック(ファイル場所の確認)

# 入力されたビデオ群の整理
if "-" in video_idx:
    video_idx = video_idx.split("-")
elif video_idx == "q":
    sys.exit(0)
else:
    video_idx = [video_idx, video_idx]
video_idx = [x for x in range(int(video_idx[0]), int(video_idx[1])+1)]
print(video_idx)

# 対象動画ファイル群の探索
file_all = os.listdir(raw_video_root)
video_set = {}
for file in file_all:
    # gopro基準の12文字出ない　もしくは　5-9文字目が対象ファイル群でない。
    if (len(file) != 12) or (file[:2] != "GX") or (not int(file[4:8]) in video_idx) or (not ".MP4" in file):
        continue
    name_temp = file[:2] + str(video_idx[0])
    # これまでに追加していない識別番号の場合、リストを生成
    if not name_temp in video_set:
        video_set[name_temp] = []
    if len(file) == 12:
        video_set[name_temp].append(file)

video_set[name_temp].sort()

for key in video_set:
    with open(f"videolist_{key}.txt", "w") as f:
        for file in video_set[key]:
            if ".MP4" in file:
                f.write(f"file '{raw_video_root}{file}'\n")

# 動画群の確認作業

# dry runできればする

# 動画のをつなげる
## できれば、フォルダに含まれるすべての動画群を直列にすべて処理できるようにする。
for key in video_set:
    if speed == "1.0":
        subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", f"videolist_{key}.txt", "-c", "copy", f"{dst_video_root}{video_output_name}.mp4"])
    else:
        subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", f"videolist_{key}.txt", "-filter:a", f'atempo={speed}', f"{dst_video_root}{video_output_name}.mp4"])
    sleep(1)

# rm videolist.txt
for key in video_set:
    os.remove(f"videolist_{key}.txt")


