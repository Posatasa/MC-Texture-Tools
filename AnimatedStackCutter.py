from PIL import Image
import os

# ===== 可配置参数 =====
input_dir = "AnimatedStackCutter_inputs"     # 输入目录
output_root = "AnimatedStackCutter_outputs"  # 输出根目录
output_ext = "png"                           # 输出格式
# =====================

os.makedirs(output_root, exist_ok=True)

# 支持的图片格式
valid_exts = (".png", ".jpg", ".jpeg", ".webp")

for filename in os.listdir(input_dir):
    if not filename.lower().endswith(valid_exts):
        continue

    input_path = os.path.join(input_dir, filename)
    base_name = os.path.splitext(filename)[0]

    print(f"\n处理文件: {filename}")

    # 打开图片
    img = Image.open(input_path)
    width, height = img.size

    frame_size = width

    # 校验是否为标准 MC 动态纹理
    if height % frame_size != 0:
        print(
            f"  跳过：高度 {height} 不能被宽度 {frame_size} 整除"
        )
        continue

    frame_count = height // frame_size
    print(f"  检测到 {frame_count} 帧")

    # 创建该图片专属输出目录
    output_dir = os.path.join(output_root, base_name)
    os.makedirs(output_dir, exist_ok=True)

    # 切分并保存
    for i in range(frame_count):
        top = i * frame_size
        bottom = top + frame_size

        frame = img.crop((0, top, width, bottom))

        output_path = os.path.join(
            output_dir,
            f"{i + 1}.{output_ext}"
        )

        frame.save(output_path)
        print(f"    已输出: {output_path}")

print("\n全部处理完成 ✔")
