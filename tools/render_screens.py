"""Render real terminal transcripts / notebook cells into screenshot PNGs."""
import glob, os, re, textwrap, json
from PIL import Image, ImageDraw, ImageFont

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F = ImageFont.truetype(MONO, 15); FB = ImageFont.truetype(MONOB, 15)
FT = ImageFont.truetype(SANS, 14)
CW = F.getbbox("M")[2]; LH = 21
BG = (24, 26, 33); FG = (220, 223, 228)
GREEN = (126, 211, 33); BLUE = (97, 175, 239); CYAN = (86, 182, 194)
YEL = (229, 192, 123); GREY = (140, 146, 156); RED = (224, 108, 117)

def wrap(lines, cols):
    out = []
    for l in lines:
        l = l.replace("\t", "    ")
        if len(l) <= cols: out.append(l)
        else:
            for i in range(0, len(l), cols): out.append(l[i:i + cols])
    return out

def color_for(line):
    if line.startswith("[maria_dev@"): return "prompt"
    if re.match(r"^(0: jdbc|\. \. \.)", line): return "beeline"
    if line.startswith("==="): return YEL
    if re.search(r"WARN|Error|ERROR", line): return RED
    if re.match(r"^\d\d/\d\d/\d\d .*INFO", line): return GREY
    if line.startswith(("+", "|")): return (200, 220, 255)
    return FG

def terminal(lines, out, title="maria_dev@sandbox-hdp: ~", cols=128, max_lines=46):
    lines = wrap(lines, cols)
    if len(lines) > max_lines:
        lines = lines[:max_lines - 2] + ["... (output truncated for screenshot) ...", lines[-1]]
    W = 40 + cols * CW; H = 50 + len(lines) * LH + 24
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 34], fill=(44, 47, 56))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([14 + i * 22, 11, 26 + i * 22, 23], fill=c)
    tw = d.textlength(title, font=FT); d.text(((W - tw) / 2, 9), title, font=FT, fill=(200, 200, 205))
    y = 46
    for l in lines:
        c = color_for(l); x = 20
        if c == "prompt":
            m = re.match(r"(\[maria_dev@sandbox-hdp [^\]]*\]\$ ?)(.*)", l)
            if m:
                d.text((x, y), m.group(1), font=FB, fill=GREEN); x += len(m.group(1)) * CW
                d.text((x, y), m.group(2), font=FB, fill=(255, 255, 255))
            else: d.text((x, y), l, font=FB, fill=GREEN)
        elif c == "beeline":
            m = re.match(r"(0: jdbc:hive2://[^>]*> |[. ]+> )(.*)", l)
            if m:
                d.text((x, y), m.group(1), font=FB, fill=CYAN); x += len(m.group(1)) * CW
                d.text((x, y), m.group(2), font=F, fill=(255, 255, 255))
            else: d.text((x, y), l, font=F, fill=CYAN)
        else:
            d.text((x, y), l, font=F, fill=c)
        y += LH
    img.save(out)

def notebook(nb_path, outdir):
    nb = json.load(open(nb_path)); n = 0; shots = []
    cells = nb["cells"]; i = 0; group = []; k = 0
    def render(group, out):
        HF = ImageFont.truetype(SANSB, 20); MF = ImageFont.truetype(SANS, 15)
        CF = ImageFont.truetype(MONO, 14); cw = CF.getbbox("M")[2]
        W = 1500; blocks = []
        for c in group:
            if c["cell_type"] == "markdown":
                txt = "".join(c["source"]).replace("**", "").replace("`", "")
                ls = []
                for l in txt.splitlines():
                    ls += textwrap.wrap(l.lstrip("# "), 150) or [""]
                blocks.append(("md", ls))
            else:
                src = "".join(c["source"]).splitlines()
                outs = []
                for o in c.get("outputs", []):
                    t = o.get("text") or o.get("data", {}).get("text/plain", "")
                    if isinstance(t, list): t = "".join(t)
                    outs += t.splitlines()
                blocks.append(("code", wrap(src, 150), wrap(outs, 150)[:40], c.get("execution_count")))
        H = 70
        for b in blocks:
            H += (len(b[1]) * 22 + 20) if b[0] == "md" else (len(b[1]) * 19 + 30 + (len(b[2]) * 19 + 16 if b[2] else 0))
        img = Image.new("RGB", (W, H + 20), (255, 255, 255)); d = ImageDraw.Draw(img)
        d.rectangle([0, 0, W, 44], fill=(243, 243, 243)); d.line([0, 44, W, 44], fill=(220, 220, 220))
        d.text((16, 12), "jupyter   penguins_elt_webhdfs.ipynb", font=ImageFont.truetype(SANSB, 16), fill=(60, 60, 60))
        d.text((W - 220, 13), "Python 3 (ipykernel)  ●", font=MF, fill=(90, 90, 90))
        y = 60
        for b in blocks:
            if b[0] == "md":
                for j, l in enumerate(b[1]):
                    d.text((110, y), l, font=HF if j == 0 else MF, fill=(30, 30, 30)); y += 22
                y += 20
            else:
                _, src, outs, ec = b
                hgt = len(src) * 19 + 14
                d.text((20, y + 6), f"In [{ec}]:", font=CF, fill=(48, 63, 159))
                d.rectangle([105, y, W - 20, y + hgt], fill=(247, 247, 247), outline=(224, 224, 224))
                yy = y + 7
                for l in src:
                    col = (0, 128, 0) if l.strip().startswith("#") else (30, 30, 30)
                    d.text((115, yy), l, font=CF, fill=col); yy += 19
                y += hgt + 16
                if outs:
                    d.text((20, y), f"Out[{ec}]:", font=CF, fill=(216, 67, 21))
                    for l in outs:
                        d.text((115, y), l, font=CF, fill=(20, 20, 20)); y += 19
                    y += 16
        img.save(out)
    # group: each markdown header with following code cells
    groups = []; cur = []
    for c in cells:
        if c["cell_type"] == "markdown" and cur:
            groups.append(cur); cur = []
        cur.append(c)
    if cur: groups.append(cur)
    for gi, g in enumerate(groups):
        p = f"{outdir}/s3_notebook_{gi+1:02d}.png"; render(g, p); shots.append(p)
    return shots

if __name__ == "__main__":
    os.makedirs("screenshots", exist_ok=True)
    for f in sorted(glob.glob("logs/*.txt")):
        name = os.path.basename(f)[:-4]
        if name.endswith("_raw") or name == "s2_full_beeline_session": continue
        lines = open(f).read().splitlines()
        title = "maria_dev@sandbox-hdp: ~/hive" if name.startswith("s2_") else "maria_dev@sandbox-hdp: ~"
        terminal(lines, f"screenshots/{name}.png", title=title)
    print(notebook("notebooks/penguins_elt_webhdfs.ipynb", "screenshots"))
