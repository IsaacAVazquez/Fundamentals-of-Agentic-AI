"""Draw a saved terminal log as a PNG that looks like the window it came from.

Used only when a real window capture is not available. Every character comes from
the log written by scripts/chat_demo.py, nothing is retyped.
Usage: .venv/bin/python scripts/render_session.py LOG PNG [TITLE]
"""
import sys

from PIL import Image, ImageDraw, ImageFont


def load_font(size):
    """Menlo on a Mac, DejaVu Sans Mono on Linux, and Pillow's built-in font anywhere else."""
    for path in ("/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


if len(sys.argv) < 3:
    sys.exit(f"usage: {sys.argv[0]} LOG PNG [TITLE]")
log, png = sys.argv[1], sys.argv[2]
title = sys.argv[3] if len(sys.argv) > 3 else "chat.py"
lines = open(log, encoding="utf-8").read().rstrip("\n").split("\n")
font = load_font(26)
pad, line_height, bar = 30, 38, 56
width = max(font.getlength(line) for line in lines + [title]) + 2 * pad
image = Image.new("RGB", (int(width), bar + pad + line_height * len(lines) + pad), (30, 30, 30))
draw = ImageDraw.Draw(image)
draw.rectangle([0, 0, image.width, bar], fill=(58, 58, 58))
for offset, color in [(28, (255, 95, 87)), (58, (255, 189, 46)), (88, (39, 201, 63))]:
    draw.ellipse([offset - 9, bar / 2 - 9, offset + 9, bar / 2 + 9], fill=color)
draw.text(((image.width - font.getlength(title)) / 2, bar / 2 - 15), title, font=font, fill=(200, 200, 200))
for index, line in enumerate(lines):
    color = (120, 220, 120) if line.startswith("You:") else (235, 235, 235)
    draw.text((pad, bar + pad + index * line_height), line, font=font, fill=color)
image.save(png)
print("wrote", png, image.size)
