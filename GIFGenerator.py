from PIL import Image
import os
import re

# ========== 配置区域 ==========
source_dir = "GIF_source"
output_dir = "GIF_Generator"

output_gif_name = "red_128.gif"  # ← 你自己改这个

# 每一帧的游戏刻数（顺序必须与图片数量一致）
ticks_per_frame = [
    3, 3, 3, 3,
    3, 3, 3, 3,
    3, 3, 3, 3,
    3, 3, 3, 3
]
# ==============================

os.makedirs(output_dir, exist_ok=True)

# ---------- 数字排序 ----------
def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else -1

files = [
    f for f in os.listdir(source_dir)
    if f.lower().endswith(".png")
]
files.sort(key=extract_number)

if len(files) != len(ticks_per_frame):
    raise ValueError(
        f"图片数量 ({len(files)}) 与 tick 数组长度 ({len(ticks_per_frame)}) 不一致"
    )

# ---------- 构建帧（按 tick 复制） ----------
frames = []

for filename, ticks in zip(files, ticks_per_frame):
    path = os.path.join(source_dir, filename)
    img = Image.open(path).convert("RGBA")

    for _ in range(ticks):
        frames.append(img.copy())

if not frames:
    raise RuntimeError("没有生成任何帧")

# ---------- 保存 GIF ----------
output_path = os.path.join(output_dir, output_gif_name)

frames[0].save(
    output_path,
    save_all=True,
    append_images=frames[1:],
    duration=50,   # 1 tick = 50ms
    loop=0,
    disposal=2
)

print(f"GIF 已生成（不会跳帧）: {output_path}")
