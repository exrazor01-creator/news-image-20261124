#!/usr/bin/env python3
"""news-image-20261124: draw one front page summing up 24 November 2026.

Pure standard library. Draws a 1024x1024 newspaper front page
("THE WORLD TODAY") with six stories from Tuesday 24 November 2026
and writes it as a deterministic PNG to /output/entry.png when
/output exists, otherwise ./entry.png.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (252, 250, 244)
INK = (18, 18, 18)
RED = (178, 34, 34)
BLUE = (28, 68, 128)
LIGHT_BLUE = (120, 170, 220)
GREY = (110, 110, 108)
DARK_GREY = (70, 70, 68)
GOLD = (176, 132, 40)
GREEN = (34, 110, 60)

# ---------------------------------------------------------------- font 5x7
# Each glyph: 7 rows of 5 bits, '1' = ink.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(img, x, y, text, scale, color):
    """Draw upper-cased text; returns x just past the last glyph."""
    text = text.upper()
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(img, cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(img, cx, y, text, scale, color):
    w = text_width(text, scale)
    draw_text(img, cx - w // 2, y, text, scale, color)


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns list of lines fitting max_width."""
    words = text.upper().split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
def new_image():
    img = bytearray(W * H * 3)
    for i in range(0, len(img), 3):
        img[i] = PAPER[0]
        img[i + 1] = PAPER[1]
        img[i + 2] = PAPER[2]
    return img


def set_pixel(img, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        img[i] = color[0]
        img[i + 1] = color[1]
        img[i + 2] = color[2]


def fill_rect(img, x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            img[i] = color[0]
            img[i + 1] = color[1]
            img[i + 2] = color[2]


def draw_hline(img, x, y, w, color, thick=1):
    fill_rect(img, x, y, w, thick, color)


def draw_vline(img, x, y, h, color, thick=1):
    fill_rect(img, x, y, thick, h, color)


def draw_line(img, x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_pixel(img, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def draw_rect_outline(img, x, y, w, h, color, thick=1):
    fill_rect(img, x, y, w, thick, color)
    fill_rect(img, x, y + h - thick, w, thick, color)
    fill_rect(img, x, y, thick, h, color)
    fill_rect(img, x + w - thick, y, thick, h, color)


def fill_circle(img, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_pixel(img, xx, yy, color)


def fill_triangle(img, ax, ay, bx, by, cx, cy, color):
    min_y = min(ay, by, cy)
    max_y = max(ay, by, cy)
    for y in range(min_y, max_y + 1):
        xs = []
        for (px, py, qx, qy) in ((ax, ay, bx, by), (bx, by, cx, cy),
                                (cx, cy, ax, ay)):
            if py == qy:
                continue
            if min(py, qy) <= y < max(py, qy) or (y == max_y and y == max(py, qy)):
                t = (y - py) / (qy - py)
                xs.append(px + t * (qx - px))
        if len(xs) >= 2:
            x0 = int(min(xs))
            x1 = int(max(xs))
            for x in range(x0, x1 + 1):
                set_pixel(img, x, y, color)


def fill_poly(img, points, color):
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)
    n = len(points)
    for y in range(min_y, max_y + 1):
        xs = []
        for i in range(n):
            px, py = points[i]
            qx, qy = points[(i + 1) % n]
            if py == qy:
                continue
            if min(py, qy) <= y < max(py, qy) or (y == max_y and y == max(py, qy)):
                t = (y - py) / (qy - py)
                xs.append(px + t * (qx - px))
        if len(xs) >= 2:
            for x in range(int(min(xs)), int(max(xs)) + 1):
                set_pixel(img, x, y, color)


# ---------------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(img, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += img[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# -------------------------------------------------------------- pictograms
def pic_ship(img, x, y, w, h):
    """Cargo ship on waves in the Strait of Hormuz."""
    sea_y = y + h - 26
    fill_rect(img, x, sea_y, w, 26, LIGHT_BLUE)
    for i in range(0, w, 26):
        draw_line(img, x + i, sea_y + 6, x + i + 13, sea_y + 12, BLUE)
        draw_line(img, x + i + 13, sea_y + 12, x + i + 26, sea_y + 6, BLUE)
    # hull
    fill_poly(img, [(x + 8, sea_y - 26), (x + w - 8, sea_y - 26),
                    (x + w - 26, sea_y), (x + 26, sea_y)], (90, 40, 30))
    # containers
    fill_rect(img, x + 22, sea_y - 62, 52, 36, RED)
    fill_rect(img, x + 78, sea_y - 62, 52, 36, BLUE)
    fill_rect(img, x + 134, sea_y - 62, 52, 36, GOLD)
    fill_rect(img, x + 190, sea_y - 62, 52, 36, GREEN)
    for cx0 in (22, 78, 134, 190):
        draw_rect_outline(img, x + cx0, sea_y - 62, 52, 36, INK, 2)
    # bridge + funnel
    fill_rect(img, x + w - 66, sea_y - 92, 44, 30, (240, 240, 235))
    draw_rect_outline(img, x + w - 66, sea_y - 92, 44, 30, INK, 2)
    fill_rect(img, x + w - 96, sea_y - 82, 16, 20, INK)
    # mast
    draw_vline(img, x + 30, sea_y - 100, 40, INK, 3)
    draw_hline(img, x + 18, sea_y - 100, 26, INK, 3)


def pic_fence(img, x, y, w, h):
    """Border fence with a closed gate."""
    gy = y + h - 18
    fill_rect(img, x, gy, w, 18, (200, 195, 180))
    # posts and rails
    for px in range(x + 6, x + w - 4, 26):
        fill_rect(img, px, y + 8, 6, gy - y - 8, DARK_GREY)
    fill_rect(img, x, y + 22, w, 6, DARK_GREY)
    fill_rect(img, x, y + 52, w, 6, DARK_GREY)
    fill_rect(img, x, y + 82, w, 6, DARK_GREY)
    for px in range(x + 12, x + w - 4, 26):
        draw_line(img, px, y + 8, px + 12, gy, GREY)
    # closed gate sign
    fill_rect(img, x + w // 2 - 52, y + 30, 104, 44, (255, 255, 255))
    draw_rect_outline(img, x + w // 2 - 52, y + 30, 104, 44, RED, 3)
    draw_text(img, x + w // 2 - 42, y + 42, "CLOSED", 2, RED)


def pic_flood(img, x, y, w, h):
    """Mountains above flood water, houses half under water."""
    # sky + mountains
    fill_triangle(img, x + 4, y + h - 40, x + w // 3, y + 6,
                  x + 2 * w // 3 - 20, y + h - 40, DARK_GREY)
    fill_triangle(img, x + w // 3, y + h - 40, x + 3 * w // 4, y + 26,
                  x + w - 4, y + h - 40, (120, 120, 116))
    fill_triangle(img, x + w // 3 - 16, y + 22, x + w // 3 + 16, y + 22,
                  x + w // 3, y + 6, (255, 255, 255))
    # flood water
    wy = y + h - 40
    fill_rect(img, x, wy, w, 40, LIGHT_BLUE)
    for i in range(0, w, 30):
        draw_line(img, x + i, wy + 12, x + i + 15, wy + 18, BLUE)
        draw_line(img, x + i + 15, wy + 18, x + i + 30, wy + 12, BLUE)
    # rooftops poking out of the water
    fill_triangle(img, x + 22, wy + 2, x + 52, wy - 22, x + 82, wy + 2, RED)
    fill_triangle(img, x + w - 96, wy + 2, x + w - 62, wy - 26,
                  x + w - 28, wy + 2, BLUE)


def pic_court(img, x, y, w, h):
    """Courthouse: pediment, columns, steps."""
    base_y = y + h - 12
    fill_triangle(img, x + 10, y + 30, x + w // 2, y + 2,
                  x + w - 10, y + 30, DARK_GREY)
    fill_circle(img, x + w // 2, y + 20, 7, GOLD)
    fill_rect(img, x + 10, y + 30, w - 20, 6, DARK_GREY)
    for cx in range(x + 26, x + w - 20, 44):
        fill_rect(img, cx, y + 36, 12, base_y - y - 52, (235, 232, 225))
        draw_rect_outline(img, cx, y + 36, 12, base_y - y - 52, INK, 1)
    fill_rect(img, x + 10, base_y - 16, w - 20, 6, DARK_GREY)
    fill_rect(img, x + 4, base_y - 8, w - 8, 6, GREY)
    fill_rect(img, x, base_y - 2, w, 6, (180, 176, 168))
    # door
    fill_rect(img, x + w // 2 - 14, base_y - 44, 28, 28, INK)


def pic_crowd(img, x, y, w, h):
    """Protest crowd with placards."""
    gy = y + h - 10
    # placards on sticks (two fit a narrow box, three a wide one)
    if w < 200:
        signs = [(x + 4, "PAY"), (x + w - 56, "FOOD")]
    else:
        signs = [(x + 16, "PAY"), (x + w // 2 - 30, "RENT"),
                 (x + w - 74, "FOOD")]
    for sx, word in signs:
        draw_vline(img, sx + 24, y + 34, gy - y - 34, DARK_GREY, 3)
        fill_rect(img, sx, y + 8, 52, 28, (255, 255, 255))
        draw_rect_outline(img, sx, y + 8, 52, 28, RED, 2)
        draw_text(img, sx + 6, y + 16, word, 1, RED)
    # heads and shoulders
    for i, hx in enumerate(range(x + 10, x + w - 8, 34)):
        fill_circle(img, hx + 12, gy - 34, 11, (232, 190, 150))
        fill_rect(img, hx, gy - 22, 24, 22, (RED, BLUE, GREEN, GOLD)[i % 4])


def pic_race(img, x, y, w, h):
    """Race car under a chequered flag, Las Vegas night."""
    fill_rect(img, x, y, w, h, (24, 24, 48))
    # chequered flag, top right
    fw = 60 if w < 200 else 84
    fh = 36 if w < 200 else 48
    fx, fy = x + w - fw - 6, y + 6
    cw, ch = fw // 6, fh // 4
    for r in range(4):
        for c in range(6):
            col = (255, 255, 255) if (r + c) % 2 == 0 else INK
            fill_rect(img, fx + c * cw, fy + r * ch, cw, ch, col)
    draw_rect_outline(img, fx, fy, fw, fh, (255, 255, 255), 2)
    draw_line(img, fx, fy + fh, fx - 8, y + h - 30, (255, 255, 255))
    # track
    fill_rect(img, x, y + h - 34, w, 34, (60, 60, 64))
    draw_hline(img, x, y + h - 18, w, (255, 220, 60), 3)
    # car body, sized to the box
    cy = y + h - 62
    nose = x + int(w * 0.08)
    tail = x + int(w * 0.94)
    mid = x + int(w * 0.30)
    fill_poly(img, [(nose, cy + 22), (mid, cy), (tail - 14, cy),
                    (tail, cy + 22)], RED)
    cab_x = x + int(w * 0.38)
    cab_w = int(w * 0.32)
    fill_rect(img, cab_x, cy - 14, cab_w, 16, RED)
    fill_rect(img, cab_x + 4, cy - 12, cab_w - 10, 12, (180, 220, 255))
    w1 = x + int(w * 0.24)
    w2 = x + int(w * 0.76)
    fill_circle(img, w1, cy + 24, 11, INK)
    fill_circle(img, w1, cy + 24, 5, (200, 200, 200))
    fill_circle(img, w2, cy + 24, 11, INK)
    fill_circle(img, w2, cy + 24, 5, (200, 200, 200))
    draw_text(img, x + int(w * 0.52), cy + 4, "1", 2, (255, 255, 255))


# ------------------------------------------------------------------- layout
MARGIN = 32
CONTENT_W = W - 2 * MARGIN

STORIES = [
    ("HORMUZ TOLL: 25 SEAFARERS DEAD",
     "UN COUNTS 25 SEAFARERS KILLED IN AND AROUND THE STRAIT OF "
     "HORMUZ SINCE THE US-ISRAEL WAR ON IRAN BEGAN IN FEBRUARY. "
     "136 INCIDENTS TRACKED BY THE IMO.",
     pic_ship),
    ("RUSSIA WARNS ESTONIA OF 'OPEN WAR'",
     "MOSCOW SAYS ESTONIA'S PLANNED BORDER CLOSURE BRINGS ACTIONS "
     "ON THE VERGE OF TRIGGERING OPEN WAR. ESTONIA PLANS TO SHUT "
     "CROSSINGS FROM 1 DECEMBER.",
     pic_fence),
    ("INDIA GIVES NEPAL $1.6BN TO REBUILD",
     "INDIA PLEDGES $1.6 BILLION TO HELP NEPAL REBUILD AFTER FLOODS.",
     pic_flood),
    ("TAJIKISTAN TO QUIT WAR-CRIMES COURT",
     "TAJIKISTAN MOVES TO LEAVE THE INTERNATIONAL CRIMINAL COURT.",
     pic_court),
    ("LISBON MARCHES OVER COST OF LIVING",
     "THOUSANDS PROTEST IN LISBON, PORTUGAL, AGAINST RISING "
     "LIVING COSTS.",
     pic_crowd),
    ("VERSTAPPEN WINS IN LAS VEGAS",
     "MAX VERSTAPPEN WON THE 2026 LAS VEGAS GRAND PRIX.",
     pic_race),
]


def draw_lead(img, story, y, height):
    headline, summary, pic = story
    draw_text(img, MARGIN, y, headline, 4, INK)
    pic_y = y + 44
    pic_h = height - 54
    pic_w = 360
    draw_rect_outline(img, MARGIN, pic_y, pic_w, pic_h, INK, 2)
    pic(img, MARGIN + 2, pic_y + 2, pic_w - 4, pic_h - 4)
    tx = MARGIN + pic_w + 20
    tw = W - MARGIN - tx
    lines = wrap_text(summary, 2, tw)
    ly = pic_y + 6
    for line in lines:
        draw_text(img, tx, ly, line, 2, DARK_GREY)
        ly += 20
    draw_text(img, tx, pic_y + pic_h - 22, "STRAIT OF HORMUZ - MIDDLE EAST",
              1, RED)
    return y + height


def draw_strip(img, story, y, height):
    headline, summary, pic = story
    pic_w = 150
    pic_h = height - 16
    draw_rect_outline(img, MARGIN, y + 8, pic_w, pic_h, INK, 2)
    pic(img, MARGIN + 2, y + 10, pic_w - 4, pic_h - 4)
    tx = MARGIN + pic_w + 18
    tw = W - MARGIN - tx
    draw_text(img, tx, y + 10, headline, 3, INK)
    lines = wrap_text(summary, 2, tw)
    ly = y + 40
    for line in lines[:3]:
        draw_text(img, tx, ly, line, 2, DARK_GREY)
        ly += 19
    return y + height


def main():
    img = new_image()
    # thin outer frame
    draw_rect_outline(img, 10, 10, W - 20, H - 20, INK, 3)

    # masthead
    draw_text_centered(img, W // 2, 30, "THE WORLD TODAY", 10, INK)
    draw_hline(img, MARGIN, 116, CONTENT_W, INK, 4)
    draw_text_centered(img, W // 2, 128, "TUESDAY, 24 NOVEMBER 2026", 2, RED)
    draw_hline(img, MARGIN, 152, CONTENT_W, INK, 2)
    draw_hline(img, MARGIN, 157, CONTENT_W, INK, 2)

    # lead story
    y = draw_lead(img, STORIES[0], 172, 252)
    draw_hline(img, MARGIN, y + 8, CONTENT_W, INK, 3)

    # five more stories as strips
    strip_y = y + 20
    strip_h = 102
    for story in STORIES[1:]:
        strip_y = draw_strip(img, story, strip_y, strip_h)
        draw_hline(img, MARGIN, strip_y - 2, CONTENT_W, GREY, 1)

    # footer
    draw_hline(img, MARGIN, 972, CONTENT_W, INK, 2)
    draw_text_centered(img, W // 2, 984,
                       "THE WORLD TODAY - TUESDAY 24 NOVEMBER 2026", 2, INK)

    out = "/output/entry.png" if os.path.isdir("/output") else "./entry.png"
    size = write_png(img, out)
    print("wrote %s (%d bytes)" % (out, size))


if __name__ == "__main__":
    main()
