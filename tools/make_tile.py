#!/usr/bin/env python3
"""Make a shortcut app's banner.png (320x180) and icon.png (192x192) with Pillow.

Text on a colour, or the person's own image fitted inside, or both background colours as a gradient:
  python3 tools/make_tile.py app/src/console/res/drawable-nodpi --text "Games Console" --bg "#D32D26"
  python3 tools/make_tile.py app/src/console/res/drawable-nodpi --image my-logo.png --bg "#F5F5F7" --scale 0.7
  python3 tools/make_tile.py app/src/desktop/res/drawable-nodpi --image logo.png --bg "#CCCECF" --bg2 "#EDEEEF"
Only use images the person supplied and has the right to use on their own TV.
"""
import argparse
import os
from PIL import Image, ImageDraw, ImageFont


def hex_rgb(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def background(w, h, c1, c2):
    im = Image.new('RGB', (w, h), c1)
    if c2:
        d = ImageDraw.Draw(im)
        for y in range(h):  # top to bottom
            t = y / max(h - 1, 1)
            d.line([(0, y), (w, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(c1, c2)))
    return im


def font(size):
    for f in ('/System/Library/Fonts/Helvetica.ttc', '/System/Library/Fonts/SFNS.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'C:/Windows/Fonts/segoeuib.ttf'):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def tile(w, h, a):
    c1 = hex_rgb(a.bg)
    im = background(w, h, c1, hex_rgb(a.bg2) if a.bg2 else None)
    if a.image:
        logo = Image.open(a.image).convert('RGBA')
        logo.thumbnail((int(w * a.scale), int(h * a.scale)), Image.LANCZOS)
        im.paste(logo, ((w - logo.width) // 2, (h - logo.height) // 2), logo)
    else:
        lum = 0.299 * c1[0] + 0.587 * c1[1] + 0.114 * c1[2]
        ink = a.fg or ('#1D1D1F' if lum > 150 else '#FFFFFF')
        d = ImageDraw.Draw(im)
        size = h // 4
        while size > 8:
            f = font(size)
            box = d.multiline_textbbox((0, 0), a.text, font=f, align='center')
            if box[2] - box[0] <= w * 0.86 and box[3] - box[1] <= h * 0.7:
                break
            size -= 2
        d.multiline_text(((w - (box[2] - box[0])) / 2 - box[0], (h - (box[3] - box[1])) / 2 - box[1]),
                         a.text, font=f, fill=ink, align='center')
    return im


ap = argparse.ArgumentParser()
ap.add_argument('out_dir')
ap.add_argument('--text')
ap.add_argument('--image')
ap.add_argument('--bg', default='#303030')
ap.add_argument('--bg2', help='second colour for a top-to-bottom gradient')
ap.add_argument('--fg', help='text colour (default: black or white, whichever reads)')
ap.add_argument('--scale', type=float, default=0.75, help='logo size inside the tile, 0-1')
a = ap.parse_args()
if not (a.text or a.image):
    ap.error('give --text or --image')
os.makedirs(a.out_dir, exist_ok=True)
tile(320, 180, a).save(os.path.join(a.out_dir, 'banner.png'))
tile(192, 192, a).save(os.path.join(a.out_dir, 'icon.png'))
print('wrote banner.png and icon.png in', a.out_dir)
