from PIL import Image
import os

# ========= 配置 =========
input_dir = "BlockbenchImageZoomer_inputs"
output_dir = "BlockbenchImageZoomer_outputs"
sizes = [32, 128]      # 输出尺寸
border_size = 1        # 透明边距像素
# ========================

os.makedirs(output_dir, exist_ok=True)

# 支持的图片格式
valid_exts = (".png", ".jpg", ".jpeg", ".webp")

for filename in os.listdir(input_dir):
    if not filename.lower().endswith(valid_exts):
        continue

    input_path = os.path.join(input_dir, filename)
    base_name = os.path.splitext(filename)[0]

    print(f"\n处理文件: {filename}")

    # 打开图片（统一转 RGBA，确保透明正确）
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size

    # ---------- 1. 补成正方形（透明补边） ----------
    side = max(w, h)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))

    offset_x = (side - w) // 2
    offset_y = (side - h) // 2

    square.paste(img, (offset_x, offset_y), img)

    # ---------- 2. 缩放 + 透明边距 ----------
    for size in sizes:
        inner_size = size - border_size * 2

        # 最近邻（硬边缘）缩放
        resized = square.resize(
            (inner_size, inner_size),
            Image.NEAREST
        )

        # 最终画布（全透明）
        final_img = Image.new(
            "RGBA",
            (size, size),
            (0, 0, 0, 0)
        )

        # 居中粘贴，形成 1px 透明边
        final_img.paste(
            resized,
            (border_size, border_size),
            resized
        )

        output_path = os.path.join(
            output_dir,
            f"{base_name}_{size}.png"
        )

        final_img.save(output_path)
        print(f"  已生成: {output_path}")

print("\n全部完成 ✔")
