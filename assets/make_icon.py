"""Generates a transparent-background 'B' monogram with a silver/chrome
gradient, so it stays legible and cool-looking against any accent theme
color used behind it in the UI."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter

SIZE = 512
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

import os
_here = os.path.dirname(os.path.abspath(__file__))
try:
    font = ImageFont.truetype(os.path.join(_here, "fonts", "Tektur-Medium.ttf"), 380)
except Exception:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 380)

draw = ImageDraw.Draw(img)
text = "B"
bbox = draw.textbbox((0, 0), text, font=font)
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx = (SIZE - w) / 2 - bbox[0]
ty = (SIZE - h) / 2 - bbox[1]

# --- text mask (the letter shape only) ---
mask = Image.new("L", (SIZE, SIZE), 0)
mdraw = ImageDraw.Draw(mask)
mdraw.text((tx, ty), text, font=font, fill=255)

# --- silver/chrome vertical gradient: dark -> bright highlight band -> mid -> dark ---
# classic brushed-metal look: highlight near the top third, darker toward the edges
stops = [
    (0.00, (150, 154, 163)),
    (0.22, (235, 238, 242)),
    (0.38, (255, 255, 255)),
    (0.55, (196, 200, 209)),
    (0.75, (150, 154, 163)),
    (1.00, (110, 114, 124)),
]

def sample(t):
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t0 <= t <= t1:
            local_t = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return tuple(int(c0[j] * (1 - local_t) + c1[j] * local_t) for j in range(3))
    return stops[-1][1]

grad = Image.new("RGB", (SIZE, SIZE))
for y in range(SIZE):
    color = sample(y / SIZE)
    for x in range(SIZE):
        grad.putpixel((x, y), color)

metal = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
metal.paste(grad, (0, 0), mask)

# subtle dark outline behind the letter for contrast on light-theme accents too
outline = Image.new("L", (SIZE, SIZE), 0)
odraw = ImageDraw.Draw(outline)
odraw.text((tx, ty), text, font=font, fill=255, stroke_width=6, stroke_fill=255)
outline_layer = Image.new("RGBA", (SIZE, SIZE), (20, 20, 25, 140))
outline_layer.putalpha(outline.filter(ImageFilter.GaussianBlur(2)))

final = Image.alpha_composite(Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0)), outline_layer)
final = Image.alpha_composite(final, metal)

final.save("/home/claude/pc-tweaker/assets/icon.png")
final.resize((256, 256)).save(
    "/home/claude/pc-tweaker/assets/icon.ico",
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)
print("silver B icon created")
