from PIL import Image
import os

# ================== 配置区 ==================
INPUT_DIR = "GIF_source"
OUTPUT_DIR = "GIF_Generator"
OUTPUT_GIF_NAME = "output.gif"

# 每两张图之间的持续刻数
# 数量必须 = 图片数量 - 1
DURATIONS = [120, 120]  # 示例：3 张图 → 2 个 duration

TICK_TIME_MS = 50  # 1 游戏刻 = 0.05s = 50ms
# ===========================================


def ease_in_out(t: float) -> float:
    """
    Minecraft 风格平滑插值（smoothstep）
    t ∈ [0, 1]
    """
    return t * t * (3 - 2 * t)


def interpolate_frames(img1: Image.Image,
                       img2: Image.Image,
                       duration_ticks: int):
    """
    在两张图片之间做 easing 插值，每 tick 一帧
    """
    frames = []

    for i in range(duration_ticks):
        t = i / duration_ticks           # 线性时间
        alpha = ease_in_out(t)           # easing
        frame = Image.blend(img1, img2, alpha)
        frames.append(frame)

    return frames


def main():
    # 读取图片
    image_files = sorted([
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

    if len(image_files) < 2:
        raise ValueError("至少需要两张图片")

    if len(DURATIONS) != len(image_files) - 1:
        raise ValueError(
            f"DURATIONS 数量应为 {len(image_files) - 1}，当前为 {len(DURATIONS)}"
        )

    images = [
        Image.open(os.path.join(INPUT_DIR, f)).convert("RGBA")
        for f in image_files
    ]

    # 确保尺寸一致（以第一张为准）
    base_size = images[0].size
    images = [img.resize(base_size, Image.NEAREST) for img in images]

    all_frames = []

    # 插值生成帧
    for i in range(len(images) - 1):
        frames = interpolate_frames(
            images[i],
            images[i + 1],
            DURATIONS[i]
        )
        all_frames.extend(frames)

    # 最后一帧补上，避免结尾闪
    all_frames.append(images[-1])

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_GIF_NAME)

    # 保存 GIF
    all_frames[0].save(
        output_path,
        save_all=True,
        append_images=all_frames[1:],
        duration=TICK_TIME_MS,
        loop=0,
        optimize=False,
        disposal=2
    )

    print(f"GIF 生成完成 ✔ -> {output_path}")
    print(f"总帧数: {len(all_frames)}")


if __name__ == "__main__":
    main()
