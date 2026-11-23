#!/usr/bin/env python3
"""
scenes_and_props.py — Complete Vector Environments, Furniture, Vehicles & Camera Transitions
Extracted from the original video ("Once You Learn To Copy You'll Never Lack Money Again")
and harmonized with the 30-Character Mouthless Bean-Body Puppet Library.
"""

import math
import random
import cairo
from puppet_30 import (
    PALETTE_CREAM,
    PALETTE_KRAFT,
    clamp,
    set_color,
    draw_rounded_rect,
    draw_star,
    draw_puppet_30,
)

def lerp(a, b, u):
    return a + (b - a) * u

# ==============================================================================
# 1. PAPER TEXTURE & DUAL-WORLD BACKGROUNDS
# ==============================================================================

def create_paper_background(width, height, world="cream"):
    pal = PALETTE_KRAFT if world == "kraft" else PALETTE_CREAM
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surf)
    set_color(ctx, pal["bg"])
    ctx.paint()

    # Soft vignette
    pat = cairo.RadialGradient(width / 2, height / 2, height * 0.35, width / 2, height / 2, width * 0.72)
    pat.add_color_stop_rgba(0, 0, 0, 0, 0.0)
    pat.add_color_stop_rgba(1, 0.12, 0.09, 0.06, 0.09)
    ctx.set_source(pat)
    ctx.paint()

    # Organic paper grain & fibers
    rng = random.Random(42 if world == "cream" else 99)
    for _ in range(1800):
        px = rng.uniform(0, width)
        py = rng.uniform(0, height)
        rad = rng.uniform(0.6, 2.2)
        set_color(ctx, pal["ink"], rng.uniform(0.02, 0.055))
        ctx.arc(px, py, rad, 0, 2 * math.pi)
        ctx.fill()

    for _ in range(300):
        px = rng.uniform(0, width)
        py = rng.uniform(0, height)
        length = rng.uniform(6, 22)
        ang = rng.uniform(0, math.pi * 2)
        set_color(ctx, pal["ink"], rng.uniform(0.015, 0.04))
        ctx.set_line_width(1.0)
        ctx.move_to(px, py)
        ctx.line_to(px + math.cos(ang) * length, py + math.sin(ang) * length)
        ctx.stroke()

    return surf

# ==============================================================================
# 2. FOREGROUND NARRATOR OVERLAY (PICTURE-IN-PICTURE HOST FROM SCREENSHOT!)
# ==============================================================================

def draw_foreground_narrator(
    ctx,
    t=0.0,
    side="right",
    archetype="classic_narrator",
    world="kraft",
    enter_progress=1.0,
    pose="idle",
):
    """
    Draws the large Foreground Narrator in the bottom-right or bottom-left corner of the frame
    (cropped at the waist by y=1080, looking toward the background scene), exactly as seen in
    the user's uploaded gas station screenshot!
    """
    if enter_progress <= 0.01:
        return

    target_x = 1660.0 if side == "right" else 260.0
    off_x = 2150.0 if side == "right" else -250.0
    nx = lerp(off_x, target_x, clamp(enter_progress))
    ny = 1265.0  # Places the bean torso and head in the lower corner (y=750..1080)
    look_x = -6.0 if side == "right" else 6.0

    ctx.save()
    ctx.identity_matrix()
    draw_puppet_30(
        ctx,
        nx,
        ny,
        scale=1.95,
        t=t,
        archetype=archetype,
        world=world,
        pose=pose,
        expression="neutral",
        look_dir=(look_x, -2.0),
    )
    ctx.restore()

# ==============================================================================
# 3. 7-SEGMENT DIGITAL DISPLAY & GAS STATION ENVIRONMENT (SCREENSHOT REPLICA!)
# ==============================================================================

DIGITS_7SEG = {
    "0": (1, 1, 1, 0, 1, 1, 1),
    "1": (0, 0, 1, 0, 0, 1, 0),
    "2": (1, 0, 1, 1, 1, 0, 1),
    "3": (1, 0, 1, 1, 0, 1, 1),
    "4": (0, 1, 1, 1, 0, 1, 0),
    "5": (1, 1, 0, 1, 0, 1, 1),
    "6": (1, 1, 0, 1, 1, 1, 1),
    "7": (1, 0, 1, 0, 0, 1, 0),
    "8": (1, 1, 1, 1, 1, 1, 1),
    "9": (1, 1, 1, 1, 0, 1, 1),
}

def draw_7seg_number(ctx, text, cx, cy, digit_w=14.0, digit_h=24.0, color=(0.96, 0.94, 0.88)):
    """Draws authentic 7-segment LCD digits like '5.20', '4.50', '3.80', '4.80'."""
    ctx.save()
    set_color(ctx, color)
    ctx.set_line_width(3.4)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    total_w = len(text) * (digit_w + 6.0) - 10.0
    cur_x = cx - total_w / 2.0
    hw = digit_w / 2.0
    hh = digit_h / 2.0

    for ch in text:
        if ch == ".":
            ctx.arc(cur_x + 2, cy + hh, 2.5, 0, 2 * math.pi)
            ctx.fill()
            cur_x += 8.0
            continue
        segs = DIGITS_7SEG.get(ch, (0, 0, 0, 0, 0, 0, 0))
        x0, x1 = cur_x, cur_x + digit_w
        y0, ym, y1 = cy - hh, cy, cy + hh
        # 0: top, 1: top-left, 2: top-right, 3: mid, 4: bot-left, 5: bot-right, 6: bot
        if segs[0]:
            ctx.move_to(x0 + 2, y0); ctx.line_to(x1 - 2, y0)
        if segs[1]:
            ctx.move_to(x0, y0 + 2); ctx.line_to(x0, ym - 1)
        if segs[2]:
            ctx.move_to(x1, y0 + 2); ctx.line_to(x1, ym - 1)
        if segs[3]:
            ctx.move_to(x0 + 2, ym); ctx.line_to(x1 - 2, ym)
        if segs[4]:
            ctx.move_to(x0, ym + 1); ctx.line_to(x0, y1 - 2)
        if segs[5]:
            ctx.move_to(x1, ym + 1); ctx.line_to(x1, y1 - 2)
        if segs[6]:
            ctx.move_to(x0 + 2, y1); ctx.line_to(x1 - 2, y1)
        ctx.stroke()
        cur_x += digit_w + 7.0
    ctx.restore()

def draw_oil_drop_emblem(ctx, cx, cy, r=36.0, pal=PALETTE_KRAFT):
    """Draws the circular cream emblem with the dark oil drop & white highlight crescent."""
    ctx.save()
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    set_color(ctx, pal["white"])
    ctx.fill()
    # Dark oil drop
    ctx.translate(cx, cy)
    ctx.scale(r / 36.0, r / 36.0)
    ctx.move_to(0, -24)
    ctx.curve_to(18, -4, 18, 18, 0, 22)
    ctx.curve_to(-18, 18, -18, -4, 0, -24)
    ctx.close_path()
    set_color(ctx, pal["ink"])
    ctx.fill()
    # Inner white reflection droplet
    ctx.move_to(-6, -6)
    ctx.curve_to(-11, 2, -10, 12, -5, 14)
    ctx.curve_to(-2, 12, -3, 2, -6, -6)
    ctx.close_path()
    set_color(ctx, pal["white"])
    ctx.fill()
    ctx.restore()

def draw_detailed_gas_station(ctx, x, y, scale=1.0, brand="red", is_closed=False, t=0.0):
    """
    Replicates the exact Gas Station from the user's screenshot:
    - Price totem with 7-segment LCD prices (5.20, 4.50, 3.80, 4.80) and oil-drop emblem
    - Canopy roof with white wave ribbon & center oil-drop emblem
    - Light-grey support pillars
    - Detailed fuel pump with dual red nozzles & curved hoses
    """
    if scale <= 0.01:
        return
    pal = PALETTE_KRAFT
    ink = pal["ink"]
    main_col = pal["red"] if brand == "red" else (0.42, 0.56, 0.32)

    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)

    # 1. Tall Price Totem (Left of canopy for Red, Right of canopy for Green)
    tx = -265.0 if brand == "red" else 265.0
    totem_w = 158.0
    draw_rounded_rect(ctx, tx - totem_w / 2, -595, totem_w, 595, 6)
    set_color(ctx, main_col)
    ctx.fill()

    # White wave across totem top + oil drop emblem
    ctx.move_to(tx - totem_w / 2, -540)
    ctx.curve_to(tx - 30, -565, tx + 30, -515, tx + totem_w / 2, -540)
    ctx.line_to(tx + totem_w / 2, -505)
    ctx.curve_to(tx + 30, -480, tx - 30, -530, tx - totem_w / 2, -505)
    ctx.close_path()
    set_color(ctx, pal["white"])
    ctx.fill()
    draw_oil_drop_emblem(ctx, tx, -535, r=42.0, pal=pal)

    # 4 Recessed Price Slats with 7-segment digits: 5.20, 4.50, 3.80, 4.80
    prices = ["5.20", "4.50", "3.80", "4.80"]
    for idx, pr in enumerate(prices):
        sy = -445 + idx * 62
        # Horizontal divider groove
        set_color(ctx, pal["bg"])
        ctx.rectangle(tx - totem_w / 2, sy - 10, totem_w, 6)
        ctx.fill()
        # Dark slate LCD box
        draw_rounded_rect(ctx, tx - 62, sy + 2, 124, 42, 5)
        set_color(ctx, ink, 0.65)
        ctx.fill()
        draw_7seg_number(ctx, pr, tx, sy + 23, digit_w=14.0, digit_h=24.0, color=pal["white"])

    # 2. Canopy Pillars (Light grey-beige columns)
    set_color(ctx, pal["light"])
    ctx.rectangle(-125, -395, 22, 395)
    ctx.rectangle(103, -395, 22, 395)
    ctx.fill()

    # 3. Canopy Roof Banner with White Wave & Oil-Drop Logo
    draw_rounded_rect(ctx, -175, -515, 350, 125, 12)
    set_color(ctx, main_col)
    ctx.fill()
    # White wave ribbon across canopy
    ctx.move_to(-175, -455)
    ctx.curve_to(-60, -485, 60, -420, 175, -455)
    ctx.line_to(175, -425)
    ctx.curve_to(60, -390, -60, -455, -175, -425)
    ctx.close_path()
    set_color(ctx, pal["white"])
    ctx.fill()
    draw_oil_drop_emblem(ctx, 0, -450, r=44.0, pal=pal)

    # 4. Detailed Fuel Pump Dispenser in Center (with Dual Red Nozzles & Hoses!)
    draw_rounded_rect(ctx, -56, -245, 112, 245, 10)
    set_color(ctx, main_col)
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(3.5)
    ctx.stroke()

    # Upper meter display box
    draw_rounded_rect(ctx, -44, -225, 88, 76, 6)
    set_color(ctx, ink, 0.72)
    ctx.fill()
    # Lower tan panel
    draw_rounded_rect(ctx, -40, -135, 80, 120, 6)
    set_color(ctx, pal["bg"], 0.85)
    ctx.fill()

    # Dual Red Fuel Nozzles & Curved Hoses on Left and Right sides of Pump
    for sign in (-1.0, 1.0):
        # Curved hose from top of pump to nozzle
        ctx.set_line_width(4.5)
        set_color(ctx, ink)
        ctx.move_to(sign * 56, -210)
        ctx.curve_to(sign * 92, -190, sign * 92, -30, sign * 74, -120)
        ctx.stroke()
        # Red nozzle holster
        ctx.save()
        ctx.translate(sign * 72, -145)
        ctx.rotate(sign * 0.22)
        draw_rounded_rect(ctx, -10, -25, 20, 52, 6)
        set_color(ctx, (0.85, 0.25, 0.22))
        ctx.fill_preserve()
        set_color(ctx, ink)
        ctx.set_line_width(3.0)
        ctx.stroke()
        ctx.restore()

    if is_closed:
        draw_rounded_rect(ctx, -52, -195, 104, 42, 6)
        set_color(ctx, pal["bg"])
        ctx.fill_preserve()
        set_color(ctx, ink)
        ctx.set_line_width(3.5)
        ctx.stroke()
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(20.0)
        ext = ctx.text_extents("CLOSED")
        ctx.move_to(-ext.width / 2, -167)
        ctx.show_text("CLOSED")

    ctx.restore()

def draw_detailed_sedan_car(
    ctx,
    x,
    y,
    scale=1.0,
    flip_x=False,
    driver_archetype="3_detective",
    world="kraft",
    t=0.0,
):
    """
    Replicates the detailed Sage-Green Sedan Car from the user's screenshot:
    - Aerodynamic sedan body with hood contour lines, bumpers, headlights, taillights, fuel cap, door handles, and side mirror
    - 6-spoke star alloy wheels inside thick dark tires
    - Transparent cabin windows showing the mouthless Bean-Body driver holding the steering wheel and waving!
    """
    if scale <= 0.01:
        return
    pal = PALETTE_KRAFT if world == "kraft" else PALETTE_CREAM
    ink = pal["ink"]
    car_green = pal["green"]

    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale * (-1.0 if flip_x else 1.0), scale)

    # 1. Cabin Interior Back Layer + Mouthless Driver Seated Inside
    ctx.save()
    # Clip driver to cabin window area
    ctx.move_to(-185, -135)
    ctx.curve_to(-135, -225, 45, -230, 145, -135)
    ctx.close_path()
    ctx.clip()

    # Background interior seat
    set_color(ctx, pal["bg"])
    ctx.paint()

    # Draw Mouthless Driver (#3 Detective with Mustache!) inside car
    draw_puppet_30(
        ctx,
        10,
        -25,
        scale=0.66,
        t=t,
        archetype=driver_archetype,
        world=world,
        pose="wave_right",
        expression="happy_eyes",
    )
    # Steering wheel
    ctx.set_line_width(6.0)
    set_color(ctx, ink)
    ctx.move_to(115, -105)
    ctx.line_to(90, -148)
    ctx.stroke()
    ctx.restore()

    # 2. Main Aerodynamic Car Chassis Path (Even-Odd fill with window cutouts so driver is visible!)
    ctx.save()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.move_to(-325, -55)
    ctx.curve_to(-335, -95, -328, -135, -310, -152)
    ctx.line_to(-215, -162)
    ctx.curve_to(-155, -235, 35, -242, 165, -142)
    ctx.curve_to(245, -132, 305, -112, 325, -88)
    ctx.curve_to(335, -68, 332, -38, 315, -32)
    ctx.line_to(-310, -32)
    ctx.close_path()

    # Rear passenger window cutout
    ctx.new_sub_path()
    ctx.move_to(-192, -142)
    ctx.curve_to(-152, -208, -75, -214, -22, -212)
    ctx.line_to(-22, -142)
    ctx.close_path()

    # Front driver window cutout (reveals driver seated inside!)
    ctx.new_sub_path()
    ctx.move_to(-8, -212)
    ctx.curve_to(52, -210, 108, -182, 152, -142)
    ctx.line_to(-8, -142)
    ctx.close_path()

    set_color(ctx, car_green)
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(4.0)
    ctx.stroke()
    ctx.restore()

    # Side mirror
    draw_rounded_rect(ctx, 118, -156, 30, 20, 8)
    set_color(ctx, car_green)
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(3.0)
    ctx.stroke()

    # 4. Authentic Details: Headlight, Taillight, Fuel Cap Circle, Door Handles & Panel Lines
    # Front Headlight
    ctx.move_to(275, -104)
    ctx.curve_to(305, -104, 322, -92, 324, -78)
    ctx.curve_to(302, -74, 282, -84, 275, -104)
    ctx.close_path()
    set_color(ctx, pal["white"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(3.0)
    ctx.stroke()

    # Rear Taillight
    ctx.move_to(-322, -135)
    ctx.line_to(-275, -132)
    ctx.curve_to(-280, -110, -305, -105, -325, -110)
    ctx.close_path()
    set_color(ctx, pal["white"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.stroke()

    # Circular Fuel Tank Cap on rear fender
    ctx.arc(-228, -118, 13, 0, 2 * math.pi)
    ctx.stroke()

    # Door Handles
    for hx in (-155, -2):
        draw_rounded_rect(ctx, hx, -124, 28, 10, 5)
        set_color(ctx, car_green)
        ctx.fill_preserve()
        set_color(ctx, ink)
        ctx.set_line_width(2.8)
        ctx.stroke()

    # 5. Front & Rear 6-Spoke Star Alloy Wheels
    for wx in (-205.0, 210.0):
        wy = -38.0
        # Dark wheel arch cutout
        ctx.arc(wx, wy, 56, math.pi, 2 * math.pi)
        set_color(ctx, ink)
        ctx.fill()
        # Tire
        ctx.arc(wx, wy, 50, 0, 2 * math.pi)
        set_color(ctx, ink)
        ctx.fill()
        # Inner cream rim
        ctx.arc(wx, wy, 32, 0, 2 * math.pi)
        set_color(ctx, pal["bg"])
        ctx.fill()
        # 6-spoke alloy star pattern rotating with time t
        ctx.save()
        ctx.translate(wx, wy)
        ctx.rotate(t * 2.5)
        set_color(ctx, ink, 0.75)
        ctx.set_line_width(5.5)
        for sp in range(6):
            ang = sp * math.pi / 3.0
            ctx.move_to(0, 0)
            ctx.line_to(math.cos(ang) * 32, math.sin(ang) * 32)
        ctx.stroke()
        ctx.arc(0, 0, 7, 0, 2 * math.pi)
        set_color(ctx, pal["bg"])
        ctx.fill()
        ctx.restore()

    ctx.restore()

# ==============================================================================
# 4. OFFICE LOBBY, SUPERMARKET, SMARTPHONE & PUZZLE METAPHORS (FROM 12-MIN VIDEO!)
# ==============================================================================

def draw_office_lobby_environment(ctx, t=0.0):
    """
    Replicates the Office Waiting Room / Glass Window Lobby from 02:12 of the original video:
    - Floor-to-ceiling glass window panes
    - Two lush potted Agave/Fern plants in tapered teal pots
    - Modern waiting bench
    """
    pal = PALETTE_CREAM
    ink = pal["ink"]
    ctx.save()

    # Glass window backdrop
    ctx.rectangle(120, 80, 1680, 620)
    set_color(ctx, pal["light"], 0.35)
    ctx.fill_preserve()
    set_color(ctx, ink, 0.45)
    ctx.set_line_width(4.0)
    ctx.stroke()
    # Vertical window mullions
    for mx in (540, 960, 1380):
        ctx.move_to(mx, 80)
        ctx.line_to(mx, 700)
    ctx.stroke()

    # Waiting Room Bench in Center
    draw_rounded_rect(ctx, 640, 560, 640, 95, 10)
    set_color(ctx, pal["mid"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(5.5)
    ctx.stroke()
    draw_rounded_rect(ctx, 620, 655, 680, 32, 8)
    set_color(ctx, pal["light"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.stroke()
    # Bench legs
    ctx.set_line_width(10.0)
    for lx in (670, 960, 1250):
        ctx.move_to(lx, 687)
        ctx.line_to(lx, 795)
    ctx.stroke()

    # Two Potted Plants (Left x=340, Right x=1580)
    for px in (340.0, 1580.0):
        py = 795.0
        # Leaves swaying gently
        for lf_idx, ang in enumerate([-0.45, -0.22, 0.0, 0.22, 0.45]):
            sway = math.sin(t * 2.2 + lf_idx) * 0.03
            ctx.save()
            ctx.translate(px, py - 145)
            ctx.rotate(ang + sway)
            ctx.move_to(0, 0)
            ctx.curve_to(-24, -110, -12, -220, 0, -285)
            ctx.curve_to(12, -220, 24, -110, 0, 0)
            ctx.close_path()
            set_color(ctx, pal["green"] if lf_idx % 2 == 0 else pal["mid"])
            ctx.fill_preserve()
            set_color(ctx, ink)
            ctx.set_line_width(4.0)
            ctx.stroke()
            ctx.restore()
        # Tapered Pot
        ctx.move_to(px - 62, py - 145)
        ctx.line_to(px + 62, py - 145)
        ctx.line_to(px + 42, py)
        ctx.line_to(px - 42, py)
        ctx.close_path()
        set_color(ctx, ink)
        ctx.fill()

    ctx.restore()

def draw_3d_book(ctx, x, y, title_line1, title_line2, subtitle, scale=1.0, angle=0.0):
    """Replicates the 3D Isometric Hardcover Book ('ONE UP ON WALL STREET') from 02:18."""
    if scale <= 0.01:
        return
    pal = PALETTE_CREAM
    ink = pal["ink"]
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.scale(scale, scale)

    # Book Spine & Back Cover
    draw_rounded_rect(ctx, -165, -215, 330, 420, 14)
    set_color(ctx, pal["mid"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(6.5)
    ctx.stroke()

    # Front Cover Panel
    draw_rounded_rect(ctx, -135, -215, 295, 395, 10)
    set_color(ctx, pal["light"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.stroke()

    # Bottom Page Edges & Gold Bookmark Ribbon
    draw_rounded_rect(ctx, -155, 175, 310, 32, 10)
    set_color(ctx, pal["white"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(5.0)
    ctx.stroke()

    # Gold bookmark ribbon
    ctx.move_to(-115, 195)
    ctx.line_to(-130, 248)
    ctx.line_to(-105, 238)
    ctx.line_to(-90, 252)
    ctx.line_to(-90, 195)
    ctx.close_path()
    set_color(ctx, pal["gold"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(4.0)
    ctx.stroke()

    # Book Title Typography
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(34.0)
    set_color(ctx, ink)
    for idx, line in enumerate([title_line1, title_line2]):
        ext = ctx.text_extents(line)
        ctx.move_to(12 - ext.width / 2, -95 + idx * 44)
        ctx.show_text(line)

    ctx.set_font_size(22.0)
    ext_s = ctx.text_extents(subtitle)
    ctx.move_to(12 - ext_s.width / 2, 35)
    ctx.show_text(subtitle)

    ctx.restore()

def draw_smartphone_feed(ctx, x, y, scale=1.0, world="kraft", scroll_offset=0.0):
    """Replicates the Giant Smartphone UI Screen from 07:10–08:30 of the original video."""
    if scale <= 0.01:
        return
    pal = PALETTE_KRAFT if world == "kraft" else PALETTE_CREAM
    ink = pal["ink"]

    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)

    # Outer Phone Bezel
    w, h = 290.0, 520.0
    draw_rounded_rect(ctx, -w / 2, -h / 2, w, h, 28)
    set_color(ctx, ink)
    ctx.fill()

    # Screen Viewport
    draw_rounded_rect(ctx, -w / 2 + 12, -h / 2 + 24, w - 24, h - 48, 16)
    set_color(ctx, pal["white"])
    ctx.fill_preserve()
    ctx.clip()

    # Top App Header Bar
    ctx.rectangle(-w / 2, -h / 2, w, 88)
    set_color(ctx, pal["red"])
    ctx.fill()

    # Scrolling Feed Cards inside screen
    for c_idx in range(4):
        cy = -120 + c_idx * 135 - (scroll_offset % 135.0)
        draw_rounded_rect(ctx, -w / 2 + 26, cy, w - 52, 112, 10)
        set_color(ctx, pal["green"] if c_idx % 2 == 0 else pal["yellow"], 0.45)
        ctx.fill_preserve()
        set_color(ctx, ink)
        ctx.set_line_width(3.5)
        ctx.stroke()
        # Thumbnail circle & text bars
        ctx.arc(-w / 2 + 68, cy + 56, 26, 0, 2 * math.pi)
        set_color(ctx, pal["red"] if c_idx % 2 == 0 else pal["mid"])
        ctx.fill()
        ctx.rectangle(-w / 2 + 110, cy + 34, 115, 14)
        ctx.rectangle(-w / 2 + 110, cy + 60, 80, 12)
        set_color(ctx, ink, 0.7)
        ctx.fill()

    ctx.restore()

def draw_puzzle_grid_2x2(ctx, cx, cy, separation=0.0, scale=1.0):
    """Replicates the 4-Piece Interlocking Mentor/Asset Puzzle from 06:15–06:35."""
    if scale <= 0.01:
        return
    pal = PALETTE_CREAM
    ink = pal["ink"]
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(scale, scale)

    offsets = [
        (-1, -1, "1. RESERVA", pal["mid"]),
        (1, -1, "2. FIIs", pal["green"]),
        (-1, 1, "3. AÇÕES", pal["gold"]),
        (1, 1, "4. JUROS", pal["light"]),
    ]
    pw, ph = 175.0, 145.0
    for (sx, sy, label, col) in offsets:
        px = sx * (pw / 2 + 6 + separation * 65.0)
        py = sy * (ph / 2 + 6 + separation * 65.0)
        draw_rounded_rect(ctx, px - pw / 2, py - ph / 2, pw, ph, 14)
        set_color(ctx, col, 0.35)
        ctx.fill_preserve()
        set_color(ctx, ink)
        ctx.set_line_width(5.5)
        ctx.stroke()

        # Puzzle tab knob
        ctx.arc(px - sx * (pw / 2), py, 20, 0, 2 * math.pi)
        set_color(ctx, col)
        ctx.fill_preserve()
        set_color(ctx, ink)
        ctx.stroke()

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(24.0)
        ext = ctx.text_extents(label)
        ctx.move_to(px - ext.width / 2, py + 8)
        ctx.show_text(label)

    ctx.restore()

# ==============================================================================
# 5. SCREEN-SPACE TRANSITIONS (3D KRAFT BOARD WIPE & BINOCULAR MASK)
# ==============================================================================

def draw_kraft_board_wipe(ctx, u_drop):
    """
    Draws the signature 3D Kraft Paper Board pulled across the screen by a sleeved arm.
    u_drop in [0.0, 1.0]: 0.0 = offscreen bottom-right, 1.0 = covering full 1920x1080 frame.
    """
    if u_drop <= 0.001 or u_drop >= 0.999:
        return
    ctx.save()
    ctx.identity_matrix()
    bx = lerp(1920.0, 0.0, u_drop)
    by = lerp(1080.0, 0.0, u_drop)

    ctx.move_to(bx - 420, by)
    ctx.line_to(1920, by - 320)
    ctx.line_to(1920, 1080)
    ctx.line_to(bx - 120, 1080)
    ctx.close_path()
    set_color(ctx, PALETTE_KRAFT["bg"])
    ctx.fill_preserve()
    set_color(ctx, PALETTE_CREAM["ink"])
    ctx.set_line_width(7.0)
    ctx.stroke()

    # Sleeved arm & hand gripping the top edge of the board
    if u_drop < 0.92:
        hx, hy = bx + 180, by - 40
        ctx.set_line_width(54.0)
        set_color(ctx, PALETTE_CREAM["ink"])
        ctx.move_to(hx + 240, hy + 220)
        ctx.line_to(hx, hy)
        ctx.stroke()
        ctx.arc(hx, hy, 32, 0, 2 * math.pi)
        set_color(ctx, PALETTE_CREAM["white"])
        ctx.fill_preserve()
        set_color(ctx, PALETTE_CREAM["ink"])
        ctx.set_line_width(5.5)
        ctx.stroke()

    ctx.restore()

def draw_binocular_mask(ctx, cx, cy, zoom_scale=1.0, alpha=1.0):
    if alpha <= 0.01 or zoom_scale <= 0.01:
        return
    ctx.save()
    ctx.identity_matrix()
    ctx.push_group()
    set_color(ctx, PALETTE_CREAM["ink"], alpha)
    ctx.rectangle(0, 0, 1920, 1080)
    ctx.fill()

    ctx.set_operator(cairo.OPERATOR_DEST_OUT)
    r = 390.0 * zoom_scale
    offset = 275.0 * zoom_scale
    ctx.arc(cx - offset, cy, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(cx + offset, cy, r, 0, 2 * math.pi)
    ctx.fill()

    ctx.pop_group_to_source()
    ctx.paint()
    ctx.restore()
