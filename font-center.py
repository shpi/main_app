import fontforge
import pathlib
import re

FONT_PATH = 'fonts/dejavu-custom.ttf'
OUTPUT_PATH = 'fonts/dejavu-custom-centered.ttf'

# Read codepoints from Icons.qml
qml_text = pathlib.Path('fonts/Icons.qml').read_text()
codepoints = [int(m, 16) for m in re.findall(r"\\\\u([0-9A-Fa-f]{4})", qml_text)]

font = fontforge.open(FONT_PATH)

# Set target metrics
em = font.em
target_width = font['A'].width
target_y_center = font.ascent - em / 2

for cp in codepoints:
    if cp not in font:
        continue
    glyph = font[cp]
    xmin, ymin, xmax, ymax = glyph.boundingBox()
    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2
    desired_x = target_width / 2
    desired_y = target_y_center
    dx = desired_x - x_center
    dy = desired_y - y_center
    glyph.transform((1, 0, 0, 1, dx, dy))
    glyph.width = target_width

font.generate(OUTPUT_PATH)
font.close()
print('Saved', OUTPUT_PATH)
