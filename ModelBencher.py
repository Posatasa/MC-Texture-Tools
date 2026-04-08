import re
import json
import os
import uuid

INPUT_DIR = "Model_Java"
OUTPUT_DIR = "Model_BB"

# ------------------------
# 工具函数
# ------------------------

def new_uuid():
    return str(uuid.uuid4())

def rad_to_deg(r):
    return r * 57.29577951308232

def safe_float(x):
    x = x.replace('F', '').replace('f', '').strip()
    try:
        return float(x)
    except:
        return None

def parse_floats(s):
    result = []
    for x in s.split(','):
        val = safe_float(x)
        if val is not None:
            result.append(val)
    return result

def fix(a, b):
    return min(a, b), max(a, b)

# ------------------------
# 解析 Java 模型（修复版）
# ------------------------

def parse_java_model(text):
    models = {}

    # ✅ 全局贴图尺寸（只认这一套）
    global_tex = [64, 64]

    for line in text.splitlines():
        line = line.strip()

        # ---------- 全局贴图尺寸 ----------
        m = re.search(r'textureWidth\s*=\s*(\d+)', line)
        if m:
            global_tex[0] = int(m.group(1))
            continue

        m = re.search(r'textureHeight\s*=\s*(\d+)', line)
        if m:
            global_tex[1] = int(m.group(1))
            continue

        # ---------- 链式 new + addBox ----------
        m = re.search(
            r'\(?\s*(\w+)\s*=\s*new ModelRenderer\(.*?,\s*(\d+),\s*(\d+)\)\)\s*\.addBox\((.*?)\)',
            line
        )
        if m:
            name = m.group(1)
            u = int(m.group(2))
            v = int(m.group(3))

            if name not in models:
                models[name] = {
                    "cubes": [],
                    "origin": [0,0,0],
                    "rotation": [0,0,0],
                    "uv": [u, v]
                }

            vals = parse_floats(m.group(4))
            if len(vals) >= 6:
                x,y,z,dx,dy,dz = vals[:6]
                models[name]["cubes"].append({
                    "from": [x,y,z],
                    "to": [x+dx,y+dy,z+dz]
                })
            continue

        # ---------- new ModelRenderer ----------
        m = re.search(r'(\w+)\s*=\s*new ModelRenderer\(.*?,\s*(\d+),\s*(\d+)\)', line)
        if m:
            name = m.group(1)
            u = int(m.group(2))
            v = int(m.group(3))

            models[name] = {
                "cubes": [],
                "origin": [0,0,0],
                "rotation": [0,0,0],
                "uv": [u, v]
            }
            continue

        # ---------- addBox ----------
        m = re.search(r'(?:this\.)?(\w+)\s*\.\s*addBox\((.*?)\)', line)
        if m:
            name = m.group(1)
            if name not in models:
                continue

            vals = parse_floats(m.group(2))
            if len(vals) >= 6:
                x,y,z,dx,dy,dz = vals[:6]
                models[name]["cubes"].append({
                    "from": [x,y,z],
                    "to": [x+dx,y+dy,z+dz]
                })
            continue

        # ---------- pivot ----------
        m = re.search(r'(?:this\.)?(\w+)\s*\.\s*setRotationPoint\((.*?)\)', line)
        if m:
            name = m.group(1)
            if name in models:
                vals = parse_floats(m.group(2))
                if len(vals) >= 3:
                    models[name]["origin"] = vals[:3]
            continue

        # ❌ 完全忽略 setTextureSize（关键修复点）
        # （不要再写这段）

        # ---------- rotateAngle ----------
        m = re.search(r'(?:this\.)?(\w+)\s*\.\s*rotateAngle([XYZ])\s*=\s*(.*?);', line)
        if m:
            name = m.group(1)
            axis = m.group(2)
            val = safe_float(m.group(3))
            if val is None:
                continue

            if name in models:
                idx = {"X":0,"Y":1,"Z":2}[axis]
                models[name]["rotation"][idx] = rad_to_deg(val)
            continue

        # ---------- setRotation ----------
        m = re.search(r'setRotation\((\w+),\s*(.*?),(.*?),(.*?)\)', line)
        if m:
            name = m.group(1)
            vals = [safe_float(m.group(i)) for i in range(2,5)]
            if name in models and all(v is not None for v in vals):
                models[name]["rotation"] = [rad_to_deg(v) for v in vals]
            continue

    return models, global_tex


# ------------------------
# 转 bbmodel（使用全局贴图）
# ------------------------

def to_bbmodel(models, global_tex):

    elements = []
    outliner = []
    groups = []

    tex_w, tex_h = global_tex  # ✅ 只用全局

    for name, data in models.items():
        group_uuid = new_uuid()

        group = {
            "name": name,
            "origin": data["origin"],
            "rotation": data["rotation"],
            "uuid": group_uuid,
            "children": []
        }

        px, py, pz = data["origin"]
        u, v = data.get("uv", [0,0])

        for cube in data["cubes"]:
            cube_uuid = new_uuid()

            fx, fy, fz = cube["from"]
            tx, ty, tz = cube["to"]

            x1, x2 = fix(-(px + fx), -(px + tx))
            y1, y2 = fix(-(py + fy), -(py + ty))
            z1, z2 = fix((pz + fz), (pz + tz))

            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            dz = abs(z2 - z1)

            element = {
                "name": name + "_cube",
                "type": "cube",
                "uuid": cube_uuid,
                "from": [x1, y1, z1],
                "to": [x2, y2, z2],
                "origin": data["origin"],
                "rotation": data["rotation"],
                "box_uv": True,
                "uv_offset": [u, v],
                "faces": {
                    "north": {"uv": [u, v+dz, u+dx, v+dz+dy]},
                    "south": {"uv": [u+dx+dz, v+dz, u+dx+dz+dx, v+dz+dy]},
                    "west":  {"uv": [u+dz, v+dz, u+dz+dx, v+dz+dy]},
                    "east":  {"uv": [u, v+dz, u+dz, v+dz+dy]},
                    "up":    {"uv": [u+dz, v, u+dz+dx, v+dz]},
                    "down":  {"uv": [u+dz+dx, v, u+dz+dx+dx, v+dz]}
                }
            }

            elements.append(element)
            group["children"].append(cube_uuid)

        groups.append(group)
        outliner.append(group_uuid)

    return {
        "meta": {
            "format_version": "5.0",
            "model_format": "modded_entity",
            "box_uv": True
        },
        "name": "converted_model",
        "resolution": {"width": tex_w, "height": tex_h},
        "elements": elements,
        "outliner": outliner,
        "groups": groups,
        "textures": []
    }


# ------------------------
# 主程序
# ------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for f in os.listdir(INPUT_DIR):
        if f.endswith(".java"):
            path = os.path.join(INPUT_DIR, f)

            with open(path, "r", encoding="utf-8") as file:
                text = file.read()

            models, global_tex = parse_java_model(text)
            bb = to_bbmodel(models, global_tex)

            out = os.path.join(OUTPUT_DIR, f.replace(".java", ".bbmodel"))
            with open(out, "w", encoding="utf-8") as o:
                json.dump(bb, o, indent=2)

            print("✔", f)

    print("\n🎉 完成（全局贴图修复版）")


if __name__ == "__main__":
    main()