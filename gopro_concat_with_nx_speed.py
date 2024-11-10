import subprocess
from time import sleep
import os, sys

raw_video_root = "your raw video saved place"
dst_video_root = "place you want to save"

video_idx = input("last 4 number of the video (xxxx-xxxx or xxxx): ").strip().replace("\n", "")
#speed = input("speed (0.5, 1.0, 2.0, ...): ").strip().replace("\n", "")
speed = 1.0
#video_output_name = input("video output name: ").strip().replace("\n", "")
video_output_name = "GX" + video_idx

file_all = os.listdir(raw_video_root)
video_set = {}

if "-" in video_idx:
    video_idx = video_idx.split("-")
elif video_idx == "q":
    sys.exit(0)
else:
    video_idx = [video_idx, video_idx]
video_idx = [x for x in range(int(video_idx[0]), int(video_idx[1])+1)]
print(video_idx)
for file in file_all:
    if (len(file) != 12) or (not int(file[4:8]) in video_idx):
        continue
    name_temp = file[:2] + str(video_idx[0])
    if (not name_temp in video_set) and (file[:2] == "GX") :
        video_set[name_temp] = []
    if file[:2] == "GX" and len(file) == 12:
        video_set[name_temp].append(file)

video_set[name_temp].sort()

for key in video_set:
    with open(f"videolist_{key}.txt", "w") as f:
        for file in video_set[key]:
            if ".MP4" in file:
                f.write(f"file '{raw_video_root}{file}'\n")

# concat videos
for key in video_set:
    if speed == "1.0":
        subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", f"videolist_{key}.txt", "-c", "copy", f"{dst_video_root}{video_output_name}.mp4"])
    else:
        subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", f"videolist_{key}.txt", "-filter:a", f'atempo={speed}', f"{dst_video_root}{video_output_name}.mp4"])
    sleep(1)

# rm videolist.txt
for key in video_set:
    os.remove(f"videolist_{key}.txt")


