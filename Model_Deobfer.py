import re
import os

INPUT_DIR = "Model_Java_Obf"
OUTPUT_DIR = "Model_Java_Deobf"

def deobfuscate(text):

    # ---------- 方法名替换 ----------
    text = re.sub(r'\bfunc_78789_a\b', 'addBox', text)
    text = re.sub(r'\bfunc_78793_a\b', 'setRotationPoint', text)
    text = re.sub(r'\bfunc_78787_b\b', 'setTextureSize', text)

    # ---------- 旋转字段 ----------
    text = re.sub(r'\bfield_78795_f\b', 'rotateAngleX', text)
    text = re.sub(r'\bfield_78796_g\b', 'rotateAngleY', text)
    text = re.sub(r'\bfield_78808_h\b', 'rotateAngleZ', text)

    # ---------- 贴图尺寸（关键！！！）----------
    text = re.sub(r'\bfield_78090_t\b', 'textureWidth', text)
    text = re.sub(r'\bfield_78089_u\b', 'textureHeight', text)

    return text


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    new_text = deobfuscate(text)

    name = os.path.basename(path)
    out_path = os.path.join(OUTPUT_DIR, name)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(new_text)

    print("✔", name)


def main():
    if not os.path.exists(INPUT_DIR):
        print("❌ 没有输入目录")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for f in os.listdir(INPUT_DIR):
        if f.endswith(".java"):
            process_file(os.path.join(INPUT_DIR, f))

    print("\n🎉 反混淆完成，可以直接丢给原版 ModelBencher.py")


if __name__ == "__main__":
    main()