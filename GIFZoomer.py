from PIL import Image, ImageSequence
import os

# ========= 配置 =========
input_dir = "GIFZoomer_inputs"
output_dir = "GIFZoomer_outputs"
sizes = [32, 128]
border_size = 1
# ========================

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if not filename.lower().endswith(".gif"):
        continue

    input_path = os.path.join(input_dir, filename)
    base_name = os.path.splitext(filename)[0]

    gif = Image.open(input_path)

    durations = []
    processed_frames = {size: [] for size in sizes}

    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")
        w, h = frame.size

        # ---------- 1. 补成正方形 ----------
        side = max(w, h)
        square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        offset_x = (side - w) // 2
        offset_y = (side - h) // 2
        square.paste(frame, (offset_x, offset_y), frame)

        # ---------- 2. 缩放 + 透明边 ----------
        for size in sizes:
            inner = size - border_size * 2
            resized = square.resize((inner, inner), Image.NEAREST)

            final_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            final_img.paste(resized, (border_size, border_size), resized)

            processed_frames[size].append(final_img)

        durations.append(frame.info.get("duration", 50))

    # ---------- 3. 输出 GIF ----------
    for size in sizes:
        output_path = os.path.join(
            output_dir,
            f"{base_name}_{size}.gif"
        )

        frames = processed_frames[size]
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            disposal=2
        )

        print(f"已生成: {output_path}")

print("全部 GIF 处理完成 ✔")
