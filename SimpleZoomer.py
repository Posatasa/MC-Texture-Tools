from PIL import Image, ImageSequence
import os

# ========== 配置 ==========
input_dir = "Zoom_space"
target_size = 128   # ← 在这里指定目标边长
# ==========================

def is_square(img):
    return img.width == img.height

for filename in os.listdir(input_dir):
    if not filename.lower().endswith((".png", ".gif")):
        continue

    path = os.path.join(input_dir, filename)

    # ---------- PNG ----------
    if filename.lower().endswith(".png"):
        img = Image.open(path)
        if not is_square(img):
            print(f"跳过非正方形 PNG: {filename}")
            continue

        resized = img.resize(
            (target_size, target_size),
            resample=Image.NEAREST
        )
        resized.save(path)

        print(f"已处理 PNG: {filename}")

    # ---------- GIF ----------
    elif filename.lower().endswith(".gif"):
        gif = Image.open(path)

        frames = []
        durations = []
        valid = True

        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert("RGBA")

            if not is_square(frame):
                valid = False
                break

            resized = frame.resize(
                (target_size, target_size),
                resample=Image.NEAREST
            )

            frames.append(resized)
            durations.append(frame.info.get("duration", 50))

        if not valid:
            print(f"跳过非正方形 GIF: {filename}")
            continue

        # 覆盖保存 GIF
        frames[0].save(
            path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            disposal=2
        )

        print(f"已处理 GIF: {filename}")

print("全部完成 ✔")
