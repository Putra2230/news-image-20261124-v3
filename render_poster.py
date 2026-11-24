#!/usr/bin/env python3
"""Render the news-image-20261124 v3 poster (build-time tool, not the entrypoint).

Own work for the 24 Nov 2026 make.fun bounty. Layout follows the newest
#1 winner's (bagarte, 22 Nov) winning ingredients -- navy top bar, red
italic headline strip, region-count chips, UTC strip, 3 illustrated heroes
beside a dark numbers panel, 10 illustrated tiles, ALSO list with a dotted
world map, two-part DATE CHECK -- but every drawing, story and layout
detail here is our own, for the 24 Nov stories. No pixels or text copied.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 14
CW = W - 2 * MARGIN  # 996

# Palette
CREAM = (247, 242, 231)
INK = (20, 20, 20)
RED = (178, 34, 34)
GREEN = (0, 110, 60)
GREY = (110, 108, 100)
SEA = (186, 214, 224)
LAND = (216, 196, 150)
NAVY = (24, 28, 36)
GOLD = (212, 175, 55)
WHITE = (255, 255, 255)
BLUE = (31, 73, 125)
TEAL = (0, 128, 128)
PURPLE = (112, 48, 160)
ORANGE = (200, 110, 20)
LIGHTGREY = (230, 226, 216)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
DEJAVU_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    for base in (FONT_DIR, DEJAVU_DIR):
        path = os.path.join(base, name)
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def serif_b(size):
    return load_font("LiberationSerif-Bold.ttf", size)


def serif(size):
    return load_font("LiberationSerif-Regular.ttf", size)


def serif_i(size):
    return load_font("LiberationSerif-Italic.ttf", size)


def sans(size):
    return load_font("LiberationSans-Regular.ttf", size)


def sans_b(size):
    return load_font("LiberationSans-Bold.ttf", size)


# ---------------------------------------------------------------- helpers
def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def wrap(draw, text, font, max_w, max_lines=None):
    """Greedy word wrap. Returns list of lines (<= max_lines if given)."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            if max_lines and len(lines) >= max_lines:
                break
    if cur and (not max_lines or len(lines) < max_lines):
        lines.append(cur)
    return lines


def wrap_no_orphan(draw, text, font, max_w, max_lines=2):
    """Wrap, then re-wrap slightly narrower if the last line is one short word."""
    lines = wrap(draw, text, font, max_w, max_lines)
    if len(lines) > 1:
        last = lines[-1].split()
        if len(last) == 1 and len(last[0]) <= 3:
            lines = wrap(draw, text, font, int(max_w * 0.92), max_lines)
    return lines


def draw_chip(draw, x, y, text, font, fg, bg=None, border=None, pad_x=5, pad_y=2):
    """Small pill label; returns its width."""
    tw = draw.textlength(text, font=font)
    w = int(tw + 2 * pad_x)
    h = font.size + 2 * pad_y + 2
    if bg is not None:
        draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    if border is not None:
        draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2,
                               outline=border, width=1)
    draw.text((x + pad_x, y + pad_y), text, font=font, fill=fg)
    return w


def draw_num_badge(draw, cx, cy, n, r=10, font=None):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE, width=1)
    f = font or sans_b(11)
    t = str(n)
    tw = draw.textlength(t, font=f)
    draw.text((cx - tw / 2, cy - f.size / 2 - 1), t, font=f, fill=WHITE)


def status_style(chip_text):
    """(fg, bg) for a source/status chip."""
    if chip_text.startswith("CONFIRMED"):
        return WHITE, GREEN
    if chip_text.startswith("REPORTED"):
        return WHITE, RED
    if chip_text.startswith("ONGOING"):
        return WHITE, BLUE
    if chip_text.startswith("CLAIM"):
        return INK, (232, 196, 60)
    return WHITE, GREY


def centre_text(draw, cx, y, text, font, fill):
    tw = draw.textlength(text, font=font)
    draw.text((cx - tw / 2, y), text, font=font, fill=fill)


# ---------------------------------------------------------------- content
HEROES = [
    dict(n=1, loc="NEW YORK", kicker="MARKETS · STOCKS",
         chip="CONFIRMED · REUTERS", scene="nvidia",
         headline="Huang is back — and Wall Street roars",
         deck="Nvidia reinstates Jensen Huang as CEO; the stock jumps 31% and lifts the S&P 5%.",
         source="CONFIRMED · REUTERS · WSJ"),
    dict(n=2, loc="TALLINN · ESTONIA", kicker="EUROPE · RUSSIA",
         chip="REPORTED · AL JAZEERA", scene="border",
         headline="Russia warns Estonia of 'open war'",
         deck="Moscow accuses Tallinn of 'hostile actions' over plans to shut every land crossing.",
         source="REPORTED · AL JAZEERA"),
    dict(n=3, loc="ANTALYA · TURKEY", kicker="GLOBAL · CLIMATE",
         chip="CONFIRMED · UN", scene="cop",
         headline="After the collapse: 'worst COP ever'",
         deck="Guterres 'deeply disappointed'; the unfinished business passes to COP32 in Ethiopia.",
         source="CONFIRMED · UN · ACT ALLIANCE"),
]

TILES = [
    dict(n=4, loc="GAZA", kicker="MIDDLE EAST · GAZA", chip="REPORTED · AP",
         scene="strike",
         headline="Israeli strikes kill UN worker in Gaza",
         deck="Others killed in the latest strikes.", source="REPORTED · AP"),
    dict(n=5, loc="WASHINGTON", kicker="N. AMERICA · USA",
         chip="REPORTED · REUTERS", scene="sanction",
         headline="US piles new Iran sanctions on",
         deck="Trump warns of a 'very traumatic' outcome.",
         source="REPORTED · REUTERS"),
    dict(n=6, loc="KATHMANDU · NEPAL", kicker="ASIA · NEPAL",
         chip="CONFIRMED · AP", scene="mountain",
         headline="India pledges $1.6bn to rebuild Nepal",
         deck="Modi–Shah reset after Himalayan floods.", source="CONFIRMED · AP"),
    dict(n=7, loc="MANCHESTER", kicker="EUROPE · UK",
         chip="REPORTED · AL JAZEERA", scene="arena",
         headline="12,000 flee concert after substance released",
         deck="Co-op Live arena evacuated.", source="REPORTED · AL JAZEERA"),
    dict(n=8, loc="LONDON", kicker="EUROPE · UK",
         chip="REPORTED · HIGH COURT", scene="crown",
         headline="Andrew 'took £750,000 bribe', court told",
         deck="Ex-prince to testify in civil trial.",
         source="REPORTED · HIGH COURT"),
    dict(n=9, loc="BRUSSELS", kicker="EUROPE · EU",
         chip="CONFIRMED · LA TIMES", scene="stars",
         headline="EU unveils sweeping Russia sanctions",
         deck="Banks, crypto and sports events targeted.",
         source="CONFIRMED · LA TIMES"),
    dict(n=10, loc="DUSHANBE", kicker="ASIA · TAJIKISTAN",
         chip="CONFIRMED · AL JAZEERA", scene="court",
         headline="Tajikistan quits the ICC",
         deck="UN notified on the day Putin visits.",
         source="CONFIRMED · AL JAZEERA"),
    dict(n=11, loc="YEREVAN · ARMENIA", kicker="EUROPE · ARMENIA",
         chip="CONFIRMED · SCMP", scene="charter",
         headline="Armenia drops Karabakh claim in new charter",
         deck="Draft constitution keys Azerbaijan peace deal.",
         source="CONFIRMED · SCMP"),
    dict(n=12, loc="GENEVA", kicker="SPORT · CHESS",
         chip="CONFIRMED · TOI", scene="chess",
         headline="Gukesh defends chess crown vs Sindarov",
         deck="World title match opens today.",
         source="CONFIRMED · TIMES OF INDIA"),
    dict(n=13, loc="WELLINGTON", kicker="SPORT · CRICKET",
         chip="CONFIRMED · TOI", scene="cricket",
         headline="India–NZ Test ends in a draw",
         deck="Visitors fight back at Basin Reserve.",
         source="CONFIRMED · TIMES OF INDIA"),
]

UTC_SLOTS = [
    ("Overnight", "Huang reinstated at Nvidia"),
    ("14:27", "Bitcoin tops $64,500"),
    ("Asia day", "India pledges $1.6bn"),
    ("Europe day", "Russia warns Estonia"),
    ("Europe day", "EU unveils sanctions"),
    ("US open", "S&P jumps 5%"),
    ("21:00", "Dow closes up 1,475"),
]

NUMBERS = [
    ("+31%", "Nvidia jump"),
    ("+5.0%", "S&P 500 day"),
    ("1,475", "Dow points gained"),
    ("$958bn", "Nvidia cap gain"),
    ("$1.6bn", "India pledge to Nepal"),
    ("12,000", "flee Manchester concert"),
]

REGION_CHIPS = [
    ("EUROPE 7", BLUE),
    ("N. AMERICA 2", RED),
    ("ASIA 2", TEAL),
    ("MIDDLE EAST 1", PURPLE),
    ("OCEANIA 1", GREEN),
]

# ALSO items: (number, region tag, region colour, text) — facts kept, words trimmed
ALSO = [
    (14, "US", RED, "Trump hosts top $TRUMP holders at private dinner"),
    (15, "US", RED, "Senate to vote on $9.4bn foreign-aid and media cuts"),
    (16, "US", RED, "Citizenship test, H-1B visa changes revealed"),
    (17, "US", RED, "Two dead, one hurt in university shooting"),
    (18, "US", RED, "Bitcoin tops $64,500 as Nvidia rally lifts crypto"),
    (19, "US", RED, "SoftBank to invest $2bn in Intel"),
    (20, "S. AMERICA", ORANGE, "Plus Ultra halts flights; Madrid–Lima, Buenos Aires cut"),
    (21, "ARGENTINA", ORANGE, "Paredes collapses on live TV after Boca's win"),
    (22, "MEXICO", RED, "National security review added to foreign investment law"),
    (23, "UK", BLUE, "UK leads global action on Myanmar after genocide ruling"),
    (24, "EU", BLUE, "Coca-Cola bottler hit by EU antitrust probe"),
    (25, "SPAIN", BLUE, "Supreme Court drops all charges against Puigdemont"),
    (26, "DENMARK", BLUE, "Supreme Court upholds 'ghetto law' evictions"),
    (27, "ANTARCTICA", TEAL, "Robot sailboats begin 5-year Southern Ocean carbon watch"),
    (28, "GREECE", BLUE, "Acropolis Museum reopens after ~20 years"),
    (29, "EU", BLUE, "'The Base' founder added to terror list"),
    (30, "AFGHANISTAN", PURPLE, "Taliban orders women's names off documents in Balkh"),
    (31, "IRAN", PURPLE, "Singer and band flogged over concert without headscarf"),
    (32, "AUSTRALIA", GREEN, "Hurricanes break WBBL duck at last"),
    (33, "INDIA", TEAL, "Modi opens AI centre at IIT Patna"),
    (34, "MOROCCO", (150, 100, 40), "Afcon 2025 title hangs on court ruling vs Senegal"),
    (35, "THAILAND", TEAL, "Thai–Cambodia border fighting on hold after truce"),
    (36, "INDONESIA", TEAL, "Factory fire toll: 24 dead, dozens missing"),
    (37, "ZIMBABWE", (150, 100, 40), "Preacher Uebert Angel arrested over sex-assault claims"),
]

DATECHECK_RULE = ("Every story on this page happened or was first reported "
                  "on Tuesday 24 November 2026 (UTC).")
DATECHECK_LEFT_OUT = [
    "COP31 talks collapse (Sun 23 Nov)",
    "UN: 25 seafarers killed at Hormuz (Fri 13 Nov)",
    "Alcaraz wins ATP Finals (Sun 22 Nov)",
    "Verstappen wins Las Vegas GP (Sun 22 Nov)",
    "BepiColombo enters Mercury orbit (Sat 21 Nov)",
    "Liverpool hammer Man Utd 4–0 (Sun 22 Nov)",
]
DATECHECK_NOT_YET = "Not yet: US confidence (10:00 ET) and Dell earnings — due today."


# ---------------------------------------------------------------- scenes
def scene_nvidia(draw, x, y, w, h):
    """Dusk skyline, green chip, rising chart, cheering figures, +31% tag."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 24, 40))
    # dusk band
    draw.rectangle([x, y, x + w, y + 14], fill=(52, 48, 86))
    # skyline blocks with lit windows
    blocks = [(0, 52, 34, 26), (36, 40, 30, 38), (68, 56, 36, 22),
              (106, 44, 30, 34), (138, 58, 34, 20), (174, 46, 30, 32),
              (206, 60, 26, 18)]
    for bx, by, bw, bh in blocks:
        draw.rectangle([x + bx, y + by, x + bx + bw, y + by + bh],
                       fill=(8, 12, 22))
        for wx in range(bx + 5, bx + bw - 3, 8):
            for wy in range(by + 5, by + bh - 3, 9):
                if (wx * 7 + wy * 3) % 11 < 6:
                    draw.rectangle([x + wx, y + wy, x + wx + 3, y + wy + 4],
                                   fill=(250, 200, 80))
    # green chip
    cx, cy = x + 52, y + 26
    draw.rounded_rectangle([cx - 26, cy - 16, cx + 26, cy + 16], radius=4,
                           fill=(0, 150, 70))
    draw.rectangle([cx - 31, cy - 4, cx - 26, cy + 4], fill=(0, 150, 70))
    draw.rectangle([cx + 26, cy - 4, cx + 31, cy + 4], fill=(0, 150, 70))
    centre_text(draw, cx, cy - 8, "NV", sans_b(13), WHITE)
    # rising chart line with arrow
    pts = [(x + 96, y + 62), (x + 128, y + 48), (x + 150, y + 52),
           (x + 178, y + 30), (x + 210, y + 18)]
    draw.line(pts, fill=(60, 220, 120), width=3)
    draw.polygon([(x + 210, y + 18), (x + 200, y + 16), (x + 206, y + 26)],
                 fill=(60, 220, 120))
    # cheering figures (small circles + arms)
    for fx in (x + 112, x + 128, x + 146):
        draw.ellipse([fx - 4, y + h - 16, fx + 4, y + h - 8], fill=WHITE)
        draw.line([(fx - 6, y + h - 20), (fx - 9, y + h - 26)], fill=WHITE, width=2)
        draw.line([(fx + 6, y + h - 20), (fx + 9, y + h - 26)], fill=WHITE, width=2)


def scene_border(draw, x, y, w, h):
    """Border crossing: sky, road, barrier, two flags, car queue, CLOSED banner."""
    draw.rectangle([x, y, x + w, y + h], fill=(196, 222, 235))
    # road
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=(90, 90, 90))
    for dx in range(6, w, 22):
        draw.rectangle([x + dx, y + h - 14, x + dx + 12, y + h - 11],
                       fill=WHITE)
    # Estonian flag (blue-black-white) on left pole
    draw.line([(x + 26, y + 8), (x + 26, y + 44)], fill=INK, width=2)
    for i, c in enumerate([(0, 114, 206), INK, WHITE]):
        draw.rectangle([x + 28, y + 8 + i * 7, x + 56, y + 15 + i * 7], fill=c)
    # Russian flag (white-blue-red) on right pole
    draw.line([(x + w - 26, y + 8), (x + w - 26, y + 44)], fill=INK, width=2)
    for i, c in enumerate([WHITE, (0, 114, 206), RED]):
        draw.rectangle([x + w - 56, y + 8 + i * 7, x + w - 28, y + 15 + i * 7],
                       fill=c)
    # barrier arm across the road
    draw.rectangle([x + 60, y + h - 52, x + w - 60, y + h - 42], fill=WHITE)
    for dx in range(62, w - 60, 16):
        draw.rectangle([x + dx, y + h - 52, x + dx + 8, y + h - 42], fill=RED)
    draw.rectangle([x + 58, y + h - 54, x + 62, y + h - 24], fill=INK)
    draw.rectangle([x + w - 62, y + h - 54, x + w - 58, y + h - 24], fill=INK)
    # car queue
    for cx in (x + 78, x + 116, x + 154):
        draw.rounded_rectangle([cx, y + h - 22, cx + 30, y + h - 10], radius=3,
                               fill=(40, 90, 160))
        draw.rectangle([cx + 6, y + h - 28, cx + 22, y + h - 21],
                       fill=(40, 90, 160))
    # CLOSED banner, left side below the flag (keeps the source chip clear)
    draw.rectangle([x + 6, y + 36, x + 68, y + 52], fill=RED)
    centre_text(draw, x + 37, y + 38, "CLOSED", sans_b(11), WHITE)


def scene_cop(draw, x, y, w, h):
    """Dark conference hall, cracked globe, empty chairs, NO DEAL banner."""
    draw.rectangle([x, y, x + w, y + h], fill=(16, 46, 52))
    # globe with crack (bigger, centre stage)
    gx, gy, gr = x + w // 2, y + 36, 27
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(40, 140, 110))
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=WHITE, width=2)
    draw.arc([gx - gr + 4, gy - gr + 4, gx + gr - 4, gy + gr - 4], 200, 340,
             fill=(220, 235, 220), width=2)
    draw.line([(gx - 5, gy - gr + 2), (gx + 3, gy - 8), (gx - 4, gy + 4),
               (gx + 5, gy + 14), (gx - 2, gy + gr - 2)], fill=WHITE, width=2)
    # empty chairs row with two delegates walking away at the sides
    for cx in range(x + 24, x + w - 24, 34):
        draw.rectangle([cx, y + h - 30, cx + 22, y + h - 12], fill=(90, 60, 40))
        draw.rectangle([cx + 2, y + h - 44, cx + 20, y + h - 30],
                       fill=(120, 80, 50))
    for dx in (x + 12, x + w - 24):
        draw.ellipse([dx, y + h - 58, dx + 10, y + h - 48], fill=(200, 200, 200))
        draw.rectangle([dx + 1, y + h - 48, dx + 9, y + h - 30],
                       fill=(200, 200, 200))
    # NO DEAL banner
    draw.rectangle([x + 10, y + 4, x + 78, y + 20], fill=RED)
    centre_text(draw, x + 44, y + 6, "NO DEAL", sans_b(11), WHITE)


def scene_strike(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 230, 235))
    for bx, bw, bh in [(6, 34, 26), (44, 28, 34), (76, 36, 22), (116, 30, 30),
                       (150, 32, 24)]:
        draw.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(120, 120, 118))
        for wy in range(y + h - bh + 5, y + h - 4, 8):
            draw.rectangle([x + bx + 5, wy, x + bx + 9, wy + 4], fill=(200, 205, 205))
    for sx, sy in [(52, 10), (140, 16)]:
        for dx, dy in [(0, -7), (6, -3), (6, 3), (0, 7), (-6, 3), (-6, -3)]:
            draw.line([(x + sx, y + sy), (x + sx + dx, y + sy + dy)],
                      fill=(230, 120, 20), width=2)
        draw.ellipse([x + sx - 3, y + sy - 3, x + sx + 3, y + sy + 3],
                     fill=(230, 120, 20))


def scene_sanction(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 214))
    draw.rectangle([x + 56, y + 4, x + w - 56, y + h - 4], fill=WHITE,
                   outline=(180, 175, 160))
    for ly in range(y + 10, y + h - 12, 7):
        draw.line([(x + 64, ly), (x + w - 64, ly)], fill=(170, 168, 160), width=1)
    # red SANCTIONED stamp, rotated look via two lines
    draw.rectangle([x + 18, y + h - 22, x + 118, y + h - 8], outline=RED, width=2)
    centre_text(draw, x + 68, y + h - 21, "SANCTIONED", sans_b(9), RED)


def scene_mountain(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(178, 212, 235))
    draw.ellipse([x + w - 30, y + 4, x + w - 12, y + 22], fill=(250, 210, 60))
    draw.polygon([(x, y + h), (x + 62, y + 8), (x + 124, y + h)], fill=(110, 118, 128))
    draw.polygon([(x + 62, y + 8), (x + 48, y + 22), (x + 76, y + 22)],
                 fill=WHITE)
    draw.polygon([(x + 96, y + h), (x + 148, y + 20), (x + w, y + h)],
                 fill=(90, 98, 110))
    draw.polygon([(x + 148, y + 20), (x + 138, y + 32), (x + 158, y + 32)],
                 fill=WHITE)
    draw.rectangle([x, y + h - 8, x + w, y + h], fill=(70, 140, 80))


def scene_arena(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(48, 32, 72))
    for sx in (x + 40, x + w // 2, x + w - 40):
        draw.polygon([(sx - 4, y), (sx + 4, y), (sx + 16, y + h - 18),
                      (sx - 16, y + h - 18)], fill=(250, 220, 90))
    draw.rectangle([x + 30, y + h - 18, x + w - 30, y + h - 8], fill=(20, 16, 30))
    for cx in range(x + 12, x + w - 8, 12):
        draw.ellipse([cx, y + h - 6, cx + 4, y + h - 2], fill=(220, 220, 220))


def scene_crown(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 30, 44))
    cx = x + w // 2
    draw.polygon([(cx - 52, y + h - 10), (cx - 52, y + 14), (cx - 26, y + 30),
                  (cx, y + 8), (cx + 26, y + 30), (cx + 52, y + 14),
                  (cx + 52, y + h - 10)], fill=(212, 175, 55))
    for px, py in [(cx - 52, 14), (cx, 8), (cx + 52, 14)]:
        draw.ellipse([px - 4, y + py - 4, px + 4, y + py + 4], fill=RED)
    draw.ellipse([cx - 5, y + 30, cx + 5, y + 40], fill=RED)
    draw.rectangle([cx - 52, y + h - 10, cx + 52, y + h - 4], fill=(170, 130, 40))


def scene_stars(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(0, 51, 102))
    cx, cy = x + w // 2, y + h // 2 + 2
    for i in range(12):
        import math
        a = math.pi * 2 * i / 12 - math.pi / 2
        sx, sy = cx + int(34 * math.cos(a)), cy + int(34 * math.sin(a))
        draw.polygon([(sx, sy - 5), (sx + 2, sy - 1), (sx + 5, sy),
                      (sx + 2, sy + 2), (sx + 1, sy + 5), (sx - 1, sy + 2),
                      (sx - 5, sy + 1), (sx - 2, sy - 2)], fill=(250, 210, 60))
    centre_text(draw, cx, cy - 9, "EU", sans_b(15), WHITE)


def scene_court(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
    cx = x + w // 2
    draw.polygon([(cx - 62, y + 16), (cx, y + 2), (cx + 62, y + 16)],
                 fill=(190, 170, 130))
    for col in (-48, -16, 16, 48):
        draw.rectangle([cx + col - 5, y + 18, cx + col + 5, y + h - 12],
                       fill=(210, 195, 160))
    draw.rectangle([cx - 66, y + h - 12, cx + 66, y + h - 6], fill=(170, 150, 110))
    # small gavel
    draw.line([(x + w - 34, y + h - 16), (x + w - 14, y + h - 26)],
              fill=(110, 70, 30), width=3)
    draw.rectangle([x + w - 38, y + h - 20, x + w - 22, y + h - 12],
                   fill=(110, 70, 30))


def scene_charter(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 234, 216))
    draw.rectangle([x + 52, y + 4, x + w - 52, y + h - 4], fill=WHITE,
                   outline=(180, 175, 160))
    for ly in range(y + 10, y + h - 12, 7):
        draw.line([(x + 60, ly), (x + w - 60, ly)], fill=(170, 168, 160), width=1)
    draw.line([(x + w - 44, y + 10), (x + w - 20, y + h - 14)], fill=INK, width=3)
    draw.polygon([(x + w - 20, y + h - 14), (x + w - 14, y + h - 8),
                  (x + w - 26, y + h - 8)], fill=RED)


def scene_chess(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(206, 178, 132))
    sq = 6
    ox, oy = x + w // 2 - 4 * sq, y + 2
    for r in range(8):
        for c in range(8):
            if (r + c) % 2 == 0:
                draw.rectangle([ox + c * sq, oy + r * sq,
                                ox + (c + 1) * sq, oy + (r + 1) * sq],
                               fill=(240, 220, 180))
            else:
                draw.rectangle([ox + c * sq, oy + r * sq,
                                ox + (c + 1) * sq, oy + (r + 1) * sq],
                               fill=(120, 82, 50))
    draw.ellipse([ox + 2 * sq + 1, oy + 1 * sq + 1, ox + 3 * sq - 1, oy + 2 * sq - 1],
                 fill=WHITE, outline=INK)
    draw.ellipse([ox + 5 * sq + 1, oy + 6 * sq + 1, ox + 6 * sq - 1, oy + 7 * sq - 1],
                 fill=INK, outline=WHITE)


def scene_cricket(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(70, 150, 80))
    draw.rectangle([x, y + h // 2 - 12, x + w, y + h // 2 + 12],
                   fill=(200, 180, 130))
    draw.line([(x + 14, y + h // 2), (x + w - 14, y + h // 2)], fill=WHITE, width=2)
    for sx in (x + 34, x + 40, x + 46):
        draw.rectangle([sx, y + h // 2 - 12, sx + 3, y + h // 2 + 2],
                       fill=(250, 210, 60))
    draw.ellipse([x + 24, y + 8, x + 34, y + 18], fill=RED)


SCENES = {
    "nvidia": scene_nvidia, "border": scene_border, "cop": scene_cop,
    "strike": scene_strike, "sanction": scene_sanction,
    "mountain": scene_mountain, "arena": scene_arena, "crown": scene_crown,
    "stars": scene_stars, "court": scene_court, "charter": scene_charter,
    "chess": scene_chess, "cricket": scene_cricket,
}


# ---------------------------------------------------------------- map
MAP_ELLIPSES = [
    (55, 46, 50, 26),    # North America
    (98, 112, 24, 32),   # South America
    (172, 32, 26, 15),   # Europe
    (182, 88, 24, 32),   # Africa
    (248, 48, 56, 30),   # Asia
    (302, 118, 22, 13),  # Australia
]
# (story number, x, y, badge offset dx, dy) in map coords
MAP_PINS = [
    (1, 48, 58, 0, 0), (5, 52, 66, 0, 0), (6, 254, 60, 0, 0),
    (10, 242, 50, 0, 0), (13, 320, 128, 0, 0),
    (7, 164, 22, -30, -16), (8, 168, 28, -18, -22), (9, 174, 32, -6, -24),
    (12, 172, 40, 10, -24), (2, 180, 22, 16, -20), (11, 194, 50, 28, -12),
    (3, 184, 50, 30, 0), (4, 190, 60, 26, 12),
]


def draw_map(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(232, 228, 218))
    # dotted land
    for gy in range(y0 + 3, y0 + h - 2, 5):
        for gx in range(x0 + 3, x0 + w - 2, 5):
            lx, ly = gx - x0, gy - y0
            for (cx, cy, rx, ry) in MAP_ELLIPSES:
                if ((lx - cx) / rx) ** 2 + ((ly - cy) / ry) ** 2 <= 1:
                    draw.ellipse([gx - 1, gy - 1, gx + 1, gy + 1],
                                 fill=(95, 100, 108))
                    break
    # ocean labels
    draw.text((x0 + 96, y0 + 84), "ATLANTIC", font=serif_i(9), fill=GREY)
    draw.text((x0 + 12, y0 + h - 16), "PACIFIC", font=serif_i(9), fill=GREY)
    draw.text((x0 + 262, y0 + 96), "INDIAN", font=serif_i(9), fill=GREY)
    # pins with leader lines for the crowded Europe cluster; badges are
    # clamped inside the map box so none protrudes past its edge
    for (n, px, py, dx, dy) in MAP_PINS:
        tx, ty = x0 + px, y0 + py
        bx, by = tx + dx, ty + dy
        bx = max(x0 + 8, min(x0 + w - 8, bx))
        by = max(y0 + 8, min(y0 + h - 8, by))
        if dx or dy:
            draw.line([(bx, by), (tx, ty)], fill=GREY, width=1)
            draw.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], fill=RED)
        draw_num_badge(draw, bx, by, n, r=7, font=sans_b(8))


# ---------------------------------------------------------------- layout
def draw_top(draw):
    draw.rectangle([MARGIN, 8, MARGIN + CW, 30], fill=NAVY)
    draw.text((MARGIN + 8, 12), "THE WORLD IN ONE DAY", font=sans_b(13),
              fill=GOLD)
    right = "37 STORIES · 7 REGIONS · ALL FROM THIS TUESDAY"
    tw = draw.textlength(right, font=sans_b(11))
    draw.text((MARGIN + CW - tw - 8, 13), right, font=sans_b(11), fill=GOLD)
    draw.text((MARGIN, 34), "Tuesday 24 November 2026",
              font=serif_b(56), fill=INK)
    draw.text((MARGIN, 98),
              "Huang is back — and Wall Street roars  ·  Russia warns Estonia "
              "of 'open war'  ·  After the collapse: 'worst COP ever'",
              font=serif_i(17), fill=RED)
    # region chips
    x = MARGIN
    for label, colour in REGION_CHIPS:
        w = draw_chip(draw, x, 124, label, sans_b(11), WHITE, colour)
        x += w + 8
    # UTC strip
    draw.rectangle([MARGIN, 152, MARGIN + CW, 176], fill=NAVY)
    draw.rectangle([MARGIN, 152, MARGIN + 46, 176], fill=RED)
    centre_text(draw, MARGIN + 23, 158, "UTC", sans_b(12), WHITE)
    slot_w = (CW - 46) / 7
    for i, (t, ev) in enumerate(UTC_SLOTS):
        sx = MARGIN + 46 + i * slot_w
        if i:
            draw.line([(sx, 156), (sx, 172)], fill=(90, 96, 110), width=1)
        draw.text((sx + 5, 155), t, font=sans_b(9), fill=GOLD)
        # event text below the time, single wrapped line
        lines = wrap(draw, ev, sans(9), slot_w - 10, 1)
        draw.text((sx + 5, 165), lines[0] if lines else "", font=sans(9),
                  fill=WHITE)


def draw_hero(draw, hero, x, y, w):
    draw_num_badge(draw, x + 10, y + 10, hero["n"], r=10, font=sans_b(11))
    draw.text((x + 26, y + 2), hero["loc"], font=sans_b(12), fill=INK)
    sy = y + 24
    SCENES[hero["scene"]](draw, x, sy, w, 98)
    fg, bg = status_style(hero["chip"])
    chip_f = sans_b(8)
    cw = draw.textlength(hero["chip"], font=chip_f) + 10
    draw.rounded_rectangle([x + w - cw - 4, sy + 4, x + w - 4, sy + 17],
                           radius=6, fill=bg)
    draw.text((x + w - cw + 1, sy + 5), hero["chip"], font=chip_f, fill=fg)
    draw.text((x, sy + 104), hero["kicker"], font=sans_b(10), fill=RED)
    lines = wrap_no_orphan(draw, hero["headline"], serif_b(17), w, 2)
    for j, ln in enumerate(lines):
        draw.text((x, sy + 120 + j * 19), ln, font=serif_b(17), fill=INK)
    dlines = wrap(draw, hero["deck"], sans(10), w, 2)
    for j, ln in enumerate(dlines):
        draw.text((x, sy + 160 + j * 12), ln, font=sans(10), fill=INK)
    draw.text((x, sy + 188), hero["source"], font=sans(9), fill=GREY)


def draw_numbers_panel(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    draw.text((x + 10, y + 8), "THE DAY IN NUMBERS", font=sans_b(12),
              fill=WHITE)
    draw.line([(x + 10, y + 30), (x + w - 10, y + 30)], fill=GOLD, width=1)
    ey = y + 38
    for num, label in NUMBERS:
        draw.text((x + 10, ey), num, font=serif_b(23), fill=GOLD)
        draw.text((x + 10, ey + 26), label, font=sans(10),
                  fill=(200, 205, 210))
        ey += 36
    return ey


def draw_tile(draw, tile, x, y, w):
    sy = y
    SCENES[tile["scene"]](draw, x, sy, w, 52)
    fg, bg = status_style(tile["chip"])
    chip_f = sans_b(7)
    cw = draw.textlength(tile["chip"], font=chip_f) + 8
    draw.rounded_rectangle([x + w - cw - 3, sy + 3, x + w - 3, sy + 14],
                           radius=5, fill=bg)
    draw.text((x + w - cw + 1, sy + 4), tile["chip"], font=chip_f, fill=fg)
    draw_num_badge(draw, x + 8, sy + 62, tile["n"], r=8, font=sans_b(9))
    draw.text((x + 20, sy + 55), tile["kicker"], font=sans_b(9), fill=RED)
    lines = wrap_no_orphan(draw, tile["headline"], sans_b(12), w, 2)
    for j, ln in enumerate(lines):
        draw.text((x, sy + 72 + j * 14), ln, font=sans_b(12), fill=INK)
    dlines = wrap(draw, tile["deck"], sans(10), w, 1)
    if dlines:
        draw.text((x, sy + 102), dlines[0], font=sans(10), fill=GREY)
    draw.text((x, sy + 116), tile["source"], font=sans(8), fill=GREY)


def also_lines_for(draw, size, col_w):
    """Return (items, total_height) for one ALSO column at given font size."""
    f_num = sans_b(size)
    f_tag = sans_b(size)
    f_txt = sans(size)
    lead = size + 1.6
    items = []
    total = 0.0
    for (n, tag, colour, text) in ALSO:
        prefix = "%d %s " % (n, tag)
        pw = draw.textlength(prefix, font=f_tag)
        lines = wrap(draw, text, f_txt, col_w - pw, 2)
        items.append((n, tag, colour, lines, pw))
        total += max(1, len(lines)) * lead
    return items, total


def draw_also_column(draw, items, x, y, size):
    f_num = sans_b(size)
    f_tag = sans_b(size)
    f_txt = sans(size)
    lead = size + 1.6
    cy = y
    for (n, tag, colour, lines, pw) in items:
        draw.text((x, cy), str(n), font=f_num, fill=RED)
        nw = draw.textlength(str(n) + " ", font=f_num)
        draw.text((x + nw, cy), tag, font=f_tag, fill=colour)
        for j, ln in enumerate(lines):
            draw.text((x + pw, cy + j * lead), ln, font=f_txt, fill=INK)
        cy += max(1, len(lines)) * lead
    return cy


def draw_bottom(draw, y0):
    # headings
    draw.text((MARGIN, y0), "ALSO ON TUESDAY 24 NOVEMBER", font=sans_b(12),
              fill=RED)
    map_x = 668
    draw.text((map_x, y0), "WHERE IT HAPPENED", font=sans_b(12), fill=RED)
    draw.text((map_x + 168, y0 + 2), "pins = story numbers", font=sans(9),
              fill=GREY)
    content_y = y0 + 16
    content_h = 924 - content_y
    col_w = 316
    # pick the largest font size that fits both columns
    chosen = None
    for size in (10.5, 10.0, 9.5, 9.0):
        left, lh = also_lines_for(draw, size, col_w)
        right, rh = also_lines_for(draw, size, col_w)
        if max(lh, rh) <= content_h:
            chosen = (size, left, right)
            break
    if chosen is None:
        size = 9.0
        left, _ = also_lines_for(draw, size, col_w)
        right, _ = also_lines_for(draw, size, col_w)
        chosen = (size, left, right)
    size, left, right = chosen
    left_items = left[:12]
    right_items = right[12:]
    draw_also_column(draw, left_items, MARGIN, content_y, size)
    draw_also_column(draw, right_items, MARGIN + col_w + 10, content_y, size)
    draw_map(draw, map_x, content_y, 342, content_h)


def draw_datecheck(draw, y0, y1):
    draw.rectangle([MARGIN, y0, MARGIN + CW, y1], outline=RED, width=2)
    # line 1: red label + rule
    label = "DATE CHECK"
    lf = sans_b(10)
    lw = draw.textlength(label, font=lf) + 12
    draw.rectangle([MARGIN + 6, y0 + 5, MARGIN + 6 + lw, y0 + 21], fill=RED)
    draw.text((MARGIN + 12, y0 + 7), label, font=lf, fill=WHITE)
    draw.text((MARGIN + 6 + lw + 8, y0 + 7), DATECHECK_RULE, font=sans(10),
              fill=INK)
    # line 2: left-out items (may wrap to 2 lines)
    pre = "Left out because they happened on an earlier day: "
    items_text = " · ".join(DATECHECK_LEFT_OUT)
    f2 = sans(9)
    full = pre + items_text
    lines = wrap(draw, full, f2, CW - 20, 2)
    ly = y0 + 24
    for ln in lines:
        draw.text((MARGIN + 10, ly), ln, font=f2, fill=INK)
        ly += 11
    draw.text((MARGIN + 10, ly + 1), DATECHECK_NOT_YET, font=sans_b(9),
              fill=RED)


def draw_footer(draw, y0):
    draw.text((MARGIN, y0), "All stories first reported Tue 24 Nov 2026.",
              font=sans_b(11), fill=INK)
    x = MARGIN + 268
    legend = [("CONFIRMED", GREEN, "on the record"),
              ("OFFICIALS", (200, 140, 30), "officials say"),
              ("REPORTED", RED, "news report"),
              ("FORECAST", BLUE, "forecast")]
    for tag, colour, expl in legend:
        w = draw_chip(draw, x, y0 - 1, tag, sans_b(8), WHITE, colour)
        x += w + 4
        tw = draw.textlength(expl, font=sans(9))
        draw.text((x, y0 + 1), expl, font=sans(9), fill=GREY)
        x += tw + 12
    draw.text((MARGIN, y0 + 15),
              "Sources: Reuters, AP, BBC, AFP, Al Jazeera, Bloomberg, "
              "LA Times, SCMP, Times of India and others.",
              font=sans(9), fill=GREY)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw_top(draw)
    # heroes + numbers panel
    hx = [MARGIN, MARGIN + 247, MARGIN + 494]
    for hero, x in zip(HEROES, hx):
        draw_hero(draw, hero, x, 184, 239)
    draw_numbers_panel(draw, 757, 184, 252, 256)
    # tiles
    tx = [MARGIN, MARGIN + 201, MARGIN + 402, MARGIN + 603, MARGIN + 804]
    for row, y in enumerate((448, 604)):
        for col, x in enumerate(tx):
            draw_tile(draw, TILES[row * 5 + col], x, y, 192)
    # divider + bottom zone
    draw.line([(MARGIN, 760), (MARGIN + CW, 760)], fill=INK, width=1)
    draw_bottom(draw, 768)
    draw_datecheck(draw, 926, 984)
    draw_footer(draw, 990)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poster.png")
    img.save(out, "PNG")
    import hashlib
    data = open(out, "rb").read()
    print("poster.png: %d bytes sha256 %s" % (len(data),
          hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
