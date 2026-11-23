#!/usr/bin/env python3
"""
puppet_30.py — Complete 30-Character Bean-Body Vector Puppet Library (60 FPS)
Follows the user's 30-character design sheets (#1 to #30) and the Original Video's MOUTHLESS rule:
- NO MOUTHS on any character (only eyes, expressive eyebrows, curved nose tick, or mustaches/beards/visors).
- Bean/Egg rounded torso (rx=49, ry=56), circular head sitting directly on top (R=45).
- Curved Bézier arms ending in 3-finger fork hands (or specialized gloves) + handheld props (squeegee, gauge, book, magnifier).
- Short curved bow-legs ending in D-shaped flat-bottom shoes (or boots/flippers/peg-leg).
- Automatic Dual-World Palette adaptation (Cream World Teal #0F4B58 vs. Kraft Storyboard Brown #3D2B24).
"""

import math
import cairo

# ==============================================================================
# DUAL-WORLD COLOR PALETTES
# ==============================================================================

PALETTE_CREAM = {
    "bg": (0.961, 0.929, 0.839),          # #F5EDD6 Warm Cream Paper
    "ink": (0.059, 0.294, 0.345),         # #0F4B58 Deep Petrol Teal Outline & Primary
    "mid": (0.325, 0.518, 0.557),         # #53848E Muted Slate Teal Secondary
    "light": (0.640, 0.765, 0.785),       # #A3C3C8 Soft Highlight Ice Teal
    "white": (0.988, 0.976, 0.933),       # #FCF9EE Off-White Face & Shirt Fill
    "gold": (0.933, 0.753, 0.235),        # #EEC03C Gold / Coins / Stars
    "green": (0.388, 0.796, 0.424),       # #63CB6C Crisp Dollar Green
    "red": (0.863, 0.325, 0.282),         # #DC5348 Coral Red Accent
    "yellow": (0.957, 0.824, 0.376),      # #F4D260 Warm Yellow Vest / Awning
}

PALETTE_KRAFT = {
    "bg": (0.780, 0.710, 0.612),          # #C7B59C Sepia Kraft Storyboard Paper
    "ink": (0.239, 0.169, 0.141),         # #3D2B24 Dark Espresso Brown Ink (from user screenshot!)
    "mid": (0.525, 0.388, 0.337),         # #866356 Muted Warm Terracotta/Brown Secondary
    "light": (0.815, 0.776, 0.725),       # #D0C6B9 Concrete / Pillar Grey-Beige
    "white": (0.965, 0.937, 0.882),       # #F6EFE1 Warm Sepia Off-White Face Fill
    "gold": (0.910, 0.745, 0.310),        # #E8BE4F Warm Gold
    "green": (0.588, 0.686, 0.490),       # #96AF7D Sage Olive Car Green (exact match to screenshot!)
    "red": (0.725, 0.345, 0.310),         # #B9584F Muted Brick Red (totem/pump nozzle)
    "yellow": (0.910, 0.773, 0.353),      # #E8C55A High-Vis Vest Mustard Yellow
}

# Alias lookup so callers can pass integer 1..30, "1", or full string name
ARCHETYPE_ALIASES = {
    1: "1_cap_gamer", "1": "1_cap_gamer", "narrator": "1_cap_gamer",
    2: "2_chef", "2": "2_chef", "chef": "2_chef",
    3: "3_detective", "3": "3_detective", "detective": "3_detective", "pabrai": "3_detective",
    4: "4_athlete", "4": "4_athlete", "athlete": "4_athlete",
    5: "5_wizard", "5": "5_wizard", "wizard": "5_wizard",
    6: "6_scientist", "6": "6_scientist", "scientist": "6_scientist", "buffett": "6_scientist",
    7: "7_engineer", "7": "7_engineer", "engineer": "7_engineer", "attendant": "7_engineer",
    8: "8_superhero", "8": "8_superhero", "superhero": "8_superhero",
    9: "9_artist", "9": "9_artist", "artist": "9_artist",
    10: "10_astronaut", "10": "10_astronaut", "astronaut": "10_astronaut",
    11: "11_ninja", "11": "11_ninja", "ninja": "11_ninja",
    12: "12_cowboy", "12": "12_cowboy", "cowboy": "12_cowboy",
    13: "13_pirate", "13": "13_pirate", "pirate": "13_pirate",
    14: "14_king", "14": "14_king", "king": "14_king",
    15: "15_firefighter", "15": "15_firefighter", "firefighter": "15_firefighter",
    16: "16_farmer", "16": "16_farmer", "farmer": "16_farmer",
    17: "17_police", "17": "17_police", "police": "17_police",
    18: "18_rockstar", "18": "18_rockstar", "rockstar": "18_rockstar",
    19: "19_samurai", "19": "19_samurai", "samurai": "19_samurai",
    20: "20_clown", "20": "20_clown", "clown": "20_clown",
    21: "21_diver", "21": "21_diver", "diver": "21_diver",
    22: "22_vampire", "22": "22_vampire", "vampire": "22_vampire",
    23: "23_boxer", "23": "23_boxer", "boxer": "23_boxer",
    24: "24_aviator", "24": "24_aviator", "aviator": "24_aviator",
    25: "25_agent", "25": "25_agent", "agent": "25_agent",
    26: "26_viking", "26": "26_viking", "viking": "26_viking",
    27: "27_football", "27": "27_football", "football": "27_football",
    28: "28_explorer", "28": "28_explorer", "explorer": "28_explorer",
    29: "29_punk", "29": "29_punk", "punk": "29_punk",
    30: "30_knight", "30": "30_knight", "knight": "30_knight",
    31: "31_student", "31": "31_student", "student": "31_student",
    32: "32_businessman", "32": "32_businessman", "businessman": "32_businessman", "office": "32_businessman",
    33: "33_barista", "33": "33_barista", "barista": "33_barista", "clerk": "33_barista",
    34: "34_courier", "34": "34_courier", "courier": "34_courier", "delivery": "34_courier",
    35: "35_professor", "35": "35_professor", "professor": "35_professor", "teacher": "35_professor",
    36: "36_tourist", "36": "36_tourist", "tourist": "36_tourist",
    37: "37_runner", "37": "37_runner", "runner": "37_runner", "gym": "37_runner",
    38: "38_waiter", "38": "38_waiter", "waiter": "38_waiter",
    39: "39_shopper", "39": "39_shopper", "shopper": "39_shopper", "customer": "39_shopper",
    40: "40_grandpa", "40": "40_grandpa", "grandpa": "40_grandpa", "retiree": "40_grandpa",
    "classic_narrator": "classic_narrator",
}

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def set_color(ctx, rgb, alpha=1.0):
    if alpha >= 0.999:
        ctx.set_source_rgb(*rgb)
    else:
        ctx.set_source_rgba(rgb[0], rgb[1], rgb[2], clamp(alpha))

def draw_rounded_rect(ctx, x, y, w, h, r):
    r = min(r, w / 2.0, h / 2.0)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()

def draw_star(ctx, cx, cy, r_outer, r_inner, points=5, rot=-math.pi / 2):
    ctx.new_sub_path()
    for i in range(points * 2):
        r = r_outer if i % 2 == 0 else r_inner
        ang = rot + i * math.pi / points
        px = cx + math.cos(ang) * r
        py = cy + math.sin(ang) * r
        if i == 0:
            ctx.move_to(px, py)
        else:
            ctx.line_to(px, py)
    ctx.close_path()

def draw_bean_torso_path(ctx, cx, cy, rx=49.0, ry=56.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(rx, ry)
    ctx.new_sub_path()
    ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
    ctx.close_path()
    ctx.restore()

def draw_fork_hand(ctx, wx, wy, angle, ink, alpha=1.0, hand_style="fork", fill_col=(1, 1, 1)):
    """Draws the 3-finger fork hand (#1-#29) or padded glove (#10 Astronaut, #23 Boxer)."""
    ctx.save()
    ctx.translate(wx, wy)
    ctx.rotate(angle)
    if hand_style == "boxer_glove":
        ctx.arc(0, 10, 18, 0, 2 * math.pi)
        set_color(ctx, fill_col, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
    elif hand_style == "mitten":
        draw_rounded_rect(ctx, -10, -2, 20, 22, 9)
        set_color(ctx, fill_col, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
    else:
        ctx.set_line_width(6.5)
        set_color(ctx, ink, alpha)
        ctx.move_to(0, 0)
        ctx.line_to(0, 15)
        ctx.move_to(0, 0)
        ctx.line_to(-10, 12)
        ctx.move_to(0, 0)
        ctx.line_to(10, 12)
        ctx.stroke()
    ctx.restore()

def draw_handheld_prop(ctx, wx, wy, prop_name, pal, alpha=1.0):
    """Draws handheld tools in the character's hand (e.g., squeegee, tire gauge, magnifier, briefcase, tray, cane, grocery_bag, water_bottle, folder, chalk)."""
    if not prop_name:
        return
    ctx.save()
    ctx.translate(wx, wy)
    ink = pal["ink"]
    if prop_name == "squeegee":
        # Long window squeegee from user's gas station screenshot!
        ctx.rotate(0.28)
        set_color(ctx, pal["light"], alpha)
        draw_rounded_rect(ctx, -4, -35, 8, 125, 3)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(3.5)
        ctx.stroke()
        draw_rounded_rect(ctx, -24, 85, 48, 12, 3)
        set_color(ctx, pal["red"], alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()
    elif prop_name == "tire_gauge":
        ctx.arc(6, 12, 18, 0, 2 * math.pi)
        set_color(ctx, pal["red"], alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.0)
        ctx.stroke()
        ctx.arc(6, 12, 11, 0, 2 * math.pi)
        set_color(ctx, pal["white"], alpha)
        ctx.fill()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(2.5)
        ctx.move_to(6, 12)
        ctx.line_to(12, 6)
        ctx.stroke()
    elif prop_name == "magnifier":
        ctx.rotate(-0.4)
        set_color(ctx, ink, alpha)
        ctx.set_line_width(7.0)
        ctx.move_to(0, 0)
        ctx.line_to(0, -38)
        ctx.stroke()
        ctx.arc(0, -68, 30, 0, 2 * math.pi)
        set_color(ctx, pal["white"], alpha * 0.55)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.5)
        ctx.stroke()
    elif prop_name == "briefcase":
        # #32 Businessman briefcase
        draw_rounded_rect(ctx, -26, 6, 52, 38, 6)
        set_color(ctx, pal["mid"], alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.5)
        ctx.stroke()
        ctx.arc(0, 6, 10, math.pi, 2 * math.pi)
        ctx.stroke()
    elif prop_name == "tray":
        # #38 Waiter tray with glass
        draw_rounded_rect(ctx, -38, -10, 76, 8, 4)
        set_color(ctx, pal["mid"], alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.0)
        ctx.stroke()
        ctx.move_to(-12, -10)
        ctx.line_to(-15, -42)
        ctx.line_to(15, -42)
        ctx.line_to(12, -10)
        ctx.close_path()
        set_color(ctx, pal["white"], alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()
    elif prop_name == "cane":
        # #40 Grandpa walking cane
        ctx.set_line_width(7.0)
        set_color(ctx, pal["mid"], alpha)
        ctx.arc(8, 12, 12, math.pi, 2 * math.pi)
        ctx.move_to(-4, 12)
        ctx.line_to(-4, 72)
        ctx.stroke()
    elif prop_name == "grocery_bag":
        # #39 Shopper paper grocery bag with baguette & greens
        draw_rounded_rect(ctx, -22, -45, 44, 54, 4)
        set_color(ctx, pal["white"], alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.5)
        ctx.stroke()
        # Baguette sticking out
        ctx.save()
        ctx.translate(8, -58)
        ctx.rotate(0.25)
        draw_rounded_rect(ctx, -8, -24, 16, 42, 8)
        set_color(ctx, pal["gold"], alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.0)
        ctx.stroke()
        ctx.restore()
    elif prop_name == "folder":
        # #31 Student notebook/folder or #35 Professor book
        ctx.rotate(0.18)
        draw_rounded_rect(ctx, -20, -32, 38, 48, 4)
        set_color(ctx, pal["white"], alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.5)
        ctx.stroke()
    ctx.restore()

# ==============================================================================
# MAIN 30-CHARACTER MOUTHLESS PUPPET DRAW FUNCTION
# ==============================================================================

def solve_2bone_ik(sh_x, sh_y, target_x, target_y, max_reach=72.0, bend_sign=1.0):
    """
    2-Bone Inverse Kinematics (IK) solver (from Codex's circuito.py):
    Computes the exact elbow control point (cx, cy) so the shoulder (sh_x, sh_y)
    and hand/finger contact point (target_x, target_y) meet at a precise world target
    with natural arm bend.
    """
    dx = target_x - sh_x
    dy = target_y - sh_y
    dist = max(1e-4, math.hypot(dx, dy))
    h = math.sqrt(max(0.0, (max_reach ** 2) - ((dist / 2.0) ** 2)))
    mid_x = (sh_x + target_x) / 2.0
    mid_y = (sh_y + target_y) / 2.0
    cx = mid_x - (dy / dist) * h * bend_sign
    cy = mid_y + (dx / dist) * h * bend_sign
    return cx, cy

def postura_bracos(pose, shoulder_y, torso_cy, hip_y, sway, wave_osc, walk_phase):
    if pose == "idle":
        el_lx, el_ly = -66.0, torso_cy + 2.0
        ha_lx, ha_ly = -66.0, hip_y - 4.0 + sway
        ang_l = 0.08
        el_rx, el_ry = 66.0, torso_cy + 2.0
        ha_rx, ha_ry = 66.0, hip_y - 4.0 - sway
        ang_r = -0.08
    elif pose == "hips":
        el_lx, el_ly = -78.0, torso_cy - 6.0
        ha_lx, ha_ly = -46.0, torso_cy + 22.0
        ang_l = -0.6
        el_rx, el_ry = 78.0, torso_cy - 6.0
        ha_rx, ha_ry = 46.0, torso_cy + 22.0
        ang_r = 0.6
    elif pose == "shrug":
        el_lx, el_ly = -68.0, torso_cy + 6.0
        ha_lx, ha_ly = -92.0, shoulder_y + 12.0 + sway
        ang_l = 2.2
        el_rx, el_ry = 68.0, torso_cy + 6.0
        ha_rx, ha_ry = 92.0, shoulder_y + 12.0 - sway
        ang_r = -2.2
    elif pose == "wave_right":
        el_lx, el_ly = -64.0, torso_cy + 2.0
        ha_lx, ha_ly = -48.0, torso_cy + 24.0
        ang_l = -0.4
        el_rx, el_ry = 76.0, shoulder_y - 6.0
        ha_rx, ha_ry = 74.0 + wave_osc, shoulder_y - 58.0
        ang_r = -2.8
    elif pose == "point_right":
        el_lx, el_ly = -64.0, torso_cy + 2.0
        ha_lx, ha_ly = -64.0, hip_y - 4.0
        ang_l = 0.08
        el_rx, el_ry = 72.0, shoulder_y + 18.0
        ha_rx, ha_ry = 104.0, shoulder_y + 2.0 + sway
        ang_r = -1.35
    elif pose == "point_left":
        el_lx, el_ly = -72.0, shoulder_y + 18.0
        ha_lx, ha_ly = -104.0, shoulder_y + 2.0 + sway
        ang_l = 1.35
        el_rx, el_ry = 64.0, torso_cy + 2.0
        ha_rx, ha_ry = 64.0, hip_y - 4.0
        ang_r = -0.08
    elif pose == "present_both":
        el_lx, el_ly = -72.0, torso_cy - 2.0
        ha_lx, ha_ly = -98.0, shoulder_y + 22.0 + sway
        ang_l = 1.65
        el_rx, el_ry = 72.0, torso_cy - 2.0
        ha_rx, ha_ry = 98.0, shoulder_y + 22.0 - sway
        ang_r = -1.65
    elif pose == "cheer":
        el_lx, el_ly = -72.0, shoulder_y - 10.0
        ha_lx, ha_ly = -84.0, shoulder_y - 54.0 + wave_osc * 0.5
        ang_l = 2.8
        el_rx, el_ry = 72.0, shoulder_y - 10.0
        ha_rx, ha_ry = 84.0, shoulder_y - 54.0 - wave_osc * 0.5
        ang_r = -2.8
    elif pose == "walk":
        swing = math.sin(walk_phase) * 22.0
        el_lx, el_ly = -62.0 - swing * 0.4, torso_cy + 2.0
        ha_lx, ha_ly = -62.0 - swing, hip_y - 6.0
        ang_l = 0.1
        el_rx, el_ry = 62.0 + swing * 0.4, torso_cy + 2.0
        ha_rx, ha_ry = 62.0 + swing, hip_y - 6.0
        ang_r = -0.1
    else:
        el_lx, el_ly = -66.0, torso_cy + 2.0
        ha_lx, ha_ly = -66.0, hip_y - 4.0
        ang_l = 0.08
        el_rx, el_ry = 66.0, torso_cy + 2.0
        ha_rx, ha_ry = 66.0, hip_y - 4.0
        ang_r = -0.08
    return (el_lx, el_ly, ha_lx, ha_ly, ang_l), (el_rx, el_ry, ha_rx, ha_ry, ang_r)


def interpolar_braco(origem, destino, peso):
    pontos = tuple(a + (b - a) * peso for a, b in zip(origem[:4], destino[:4]))
    delta = (destino[4] - origem[4] + math.pi) % (2 * math.pi) - math.pi
    return (*pontos, origem[4] + delta * peso)


def contato_braco(origem, ombro, alvo, peso, dobra):
    if alvo is None or peso <= 0:
        return origem
    tx, ty = alvo
    ex, ey = solve_2bone_ik(*ombro, tx, ty, max_reach=68.0, bend_sign=dobra)
    destino = (ex, ey, tx, ty, math.atan2(ty - ey, tx - ex) - math.pi / 2.0)
    return interpolar_braco(origem, destino, peso) if peso < 1 else destino


def draw_puppet_30(
    ctx,
    x,
    y,
    scale=1.0,
    t=0.0,
    archetype="1_cap_gamer",
    world="cream",
    alpha=1.0,
    pose="idle",
    facing=1.0,
    expression="neutral",
    walk_phase=0.0,
    look_dir=(0.0, 0.0),
    prop_l=None,
    prop_r=None,
    high_vis_vest=False,
    ik_hand_l=None,
    ik_hand_r=None,
    *,
    pose_anterior=None,
    peso_pose=1.0,
    peso_ik_l=1.0,
    peso_ik_r=1.0,
):
    """
    Draws a mouthless Bean-Body character at ground position (x, y).
    IK targets are wrist anchors in rig coordinates before scale and facing.
    """
    if scale <= 0.01 or alpha <= 0.01:
        return

    arch = ARCHETYPE_ALIASES.get(archetype, str(archetype))
    pal = PALETTE_KRAFT if world == "kraft" else PALETTE_CREAM
    ink = pal["ink"]
    mid = pal["mid"]
    white = pal["white"]

    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale * facing, scale)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    seed = (int(abs(x * 13 + y * 7)) % 100) * 0.1
    breath = math.sin(t * 3.4 + seed) * 2.5
    head_bob = math.sin(t * 3.4 + seed - 0.4) * 2.5
    walk_bounce = abs(math.sin(walk_phase)) * 7.5 if pose == "walk" else 0.0

    hip_y = -66.0 + breath * 0.3 - walk_bounce
    torso_cy = -120.0 + breath * 0.7 - walk_bounce
    shoulder_y = -158.0 + breath - walk_bounce
    head_cy = -218.0 + breath + head_bob - walk_bounce
    head_r = 45.0

    # ------------------------------------------------------------------
    # 0. BACK LAYER (Capes, Swords, Guitars, Viking Shields, Diver Tanks)
    # ------------------------------------------------------------------
    if arch in ("8_superhero", "22_vampire"):
        flutter = math.sin(t * 5.5 + seed) * 9.0
        ctx.move_to(-34, shoulder_y + 4)
        ctx.curve_to(-58, torso_cy + 10, -64, -22, -24, -15 + flutter * 0.3)
        ctx.curve_to(25, -8, 72, -14, 112 + flutter, -34 - flutter * 0.4)
        ctx.curve_to(82, -74, 56, shoulder_y + 12, 34, shoulder_y + 4)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.0)
        ctx.stroke()

    elif arch == "14_king":
        ctx.move_to(-42, shoulder_y + 4)
        ctx.curve_to(-65, torso_cy, -75, -35, -82, -8)
        ctx.line_to(82, -8)
        ctx.curve_to(75, -35, 65, torso_cy, 42, shoulder_y + 4)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.5)
        ctx.stroke()

    elif arch == "11_ninja":
        # Katana sword handle sticking diagonally behind right shoulder
        ctx.save()
        ctx.translate(28, shoulder_y + 8)
        ctx.rotate(0.65)
        draw_rounded_rect(ctx, -6, -68, 12, 65, 3)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.0)
        ctx.stroke()
        ctx.restore()

    elif arch in ("10_astronaut", "21_diver", "31_student", "34_courier"):
        bw = 122 if arch == "34_courier" else 108
        bh = 104 if arch == "34_courier" else 90
        draw_rounded_rect(ctx, -bw / 2, shoulder_y - 10, bw, bh, 14)
        set_color(ctx, mid if arch in ("10_astronaut", "34_courier") else white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.0)
        ctx.stroke()

    # ------------------------------------------------------------------
    # 1. SHORT BOW-LEGS & ARCHETYPE FOOTWEAR
    # ------------------------------------------------------------------
    if pose == "walk":
        stride = math.sin(walk_phase) * 20.0
        lift_l = max(0.0, math.cos(walk_phase)) * 10.0
        lift_r = max(0.0, -math.cos(walk_phase)) * 10.0
        foot_lx, foot_ly = -26.0 + stride, -lift_l
        foot_rx, foot_ry = 26.0 - stride, -lift_r
        knee_lx = -34.0 + stride * 0.5
        knee_rx = 34.0 - stride * 0.5
    else:
        foot_lx, foot_ly = -28.0, 0.0
        foot_rx, foot_ry = 28.0, 0.0
        knee_lx = -37.0
        knee_rx = 37.0

    ctx.set_line_width(7.0)
    set_color(ctx, ink, alpha)

    # Left leg
    ctx.move_to(-26.0, hip_y)
    ctx.curve_to(knee_lx, (hip_y + foot_ly) * 0.5, knee_lx, (hip_y + foot_ly) * 0.75, foot_lx, foot_ly - 4)
    ctx.stroke()

    # Right leg (or Pirate Peg-Leg #13)
    if arch == "13_pirate":
        ctx.move_to(20.0, hip_y - 4)
        ctx.line_to(26.0, hip_y - 4)
        ctx.line_to(24.0, foot_ry - 3)
        ctx.line_to(18.0, foot_ry - 3)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
    else:
        ctx.move_to(26.0, hip_y)
        ctx.curve_to(knee_rx, (hip_y + foot_ry) * 0.5, knee_rx, (hip_y + foot_ry) * 0.75, foot_rx, foot_ry - 4)
        ctx.stroke()

    shoe_list = [(foot_lx, foot_ly, -1.0)]
    if arch != "13_pirate":
        shoe_list.append((foot_rx, foot_ry, 1.0))

    for fx, fy, dir_sign in shoe_list:
        ctx.save()
        ctx.translate(fx + dir_sign * 3.0, fy)
        if arch == "21_diver":
            # Scuba Flippers (#21)
            ctx.move_to(0, -8)
            ctx.line_to(38 * dir_sign, 2)
            ctx.line_to(24 * dir_sign, 10)
            ctx.line_to(-8 * dir_sign, -2)
            ctx.close_path()
            set_color(ctx, mid, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.0)
            ctx.stroke()
        elif arch in ("10_astronaut", "12_cowboy", "16_farmer", "24_aviator", "26_viking", "28_explorer", "30_knight"):
            # Symmetric Chunky Boot
            ctx.move_to(-12, -26)
            ctx.line_to(12, -26)
            ctx.line_to(13, -10)
            ctx.line_to(17 * dir_sign, -6)
            ctx.line_to(17 * dir_sign, 0)
            ctx.line_to(-13 * dir_sign, 0)
            ctx.line_to(-13, -10)
            ctx.close_path()
            set_color(ctx, white if arch in ("10_astronaut", "30_knight") else mid, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.5)
            ctx.stroke()
        else:
            # Standard D-shaped half-pill shoe
            ctx.new_sub_path()
            ctx.arc(0, 0, 13.5, math.pi, 2 * math.pi)
            ctx.close_path()
            set_color(ctx, white if arch == "4_athlete" else mid, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.5)
            ctx.stroke()
        ctx.restore()

    # ------------------------------------------------------------------
    # 2. BEAN-BODY TORSO & OUTFIT DETAILS FOR ALL 30 ARCHETYPES
    # ------------------------------------------------------------------
    ctx.save()

    # Determine base bean torso color
    white_beans = ("4_athlete", "8_superhero", "9_artist", "10_astronaut", "12_cowboy", "13_pirate", "16_farmer", "20_clown", "23_boxer", "28_explorer", "29_punk", "30_knight", "32_businessman", "33_barista", "36_tourist", "37_runner")
    mid_beans = ("3_detective", "6_scientist", "7_engineer", "17_police", "19_samurai", "21_diver", "24_aviator", "26_viking", "27_football", "31_student", "34_courier", "35_professor", "38_waiter", "39_shopper", "40_grandpa")

    if arch in ("5_wizard", "25_agent"):
        # Flared full-length coat/robe (#5 Wizard, #25 Agent)
        ctx.move_to(-32, shoulder_y + 4)
        ctx.line_to(-52, hip_y + 10)
        ctx.curve_to(-20, hip_y + 18, 20, hip_y + 18, 52, hip_y + 10)
        ctx.line_to(32, shoulder_y + 4)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.5)
        ctx.stroke()
        ctx.move_to(0, torso_cy - 12)
        ctx.line_to(0, hip_y + 14)
        ctx.stroke()
    else:
        base_col = white if arch in white_beans else (mid if arch in mid_beans else ink)
        draw_bean_torso_path(ctx, 0, torso_cy, rx=49, ry=56)
        set_color(ctx, base_col, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.5)
        ctx.stroke()

    # Archetype-specific torso overlays
    if arch == "classic_narrator":
        # White crew-neck scoop from original video narrator
        ctx.move_to(-25, shoulder_y + 2)
        ctx.curve_to(-14, shoulder_y + 28, 14, shoulder_y + 28, 25, shoulder_y + 2)
        ctx.close_path()
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.0)
        ctx.stroke()

    elif arch in ("2_chef", "33_barista"):
        ctx.move_to(-26, shoulder_y + 8)
        ctx.line_to(26, shoulder_y + 8)
        ctx.line_to(36, hip_y + 4)
        ctx.line_to(-36, hip_y + 4)
        ctx.close_path()
        set_color(ctx, mid if arch == "33_barista" else white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        if arch == "33_barista":
            # Name tag badge on barista apron
            draw_rounded_rect(ctx, 6, torso_cy - 18, 22, 14, 3)
            set_color(ctx, white, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(3.5)
            ctx.stroke()
        else:
            ctx.arc(0, torso_cy + 14, 17, 0, math.pi)
            ctx.close_path()
            ctx.stroke()

    elif arch in ("3_detective", "25_agent"):
        # High trench collar + V-neck tie
        ctx.move_to(-30, shoulder_y + 12)
        ctx.line_to(-46, shoulder_y - 10)
        ctx.line_to(-18, shoulder_y - 6)
        ctx.line_to(0, shoulder_y + 18)
        ctx.line_to(18, shoulder_y - 6)
        ctx.line_to(46, shoulder_y - 10)
        ctx.line_to(30, shoulder_y + 12)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()

    elif arch == "4_athlete":
        # Horizontal chest stripe & dark shorts
        ctx.rectangle(-47, torso_cy - 6, 94, 18)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.0)
        ctx.stroke()
        ctx.arc(0, torso_cy, 49, 0.2 * math.pi, 0.8 * math.pi)
        ctx.close_path()
        set_color(ctx, ink, alpha)
        ctx.fill()

    elif arch == "6_scientist":
        for sign in (-1.0, 1.0):
            ctx.move_to(sign * 14, shoulder_y + 4)
            ctx.curve_to(sign * 46, shoulder_y + 10, sign * 54, torso_cy, sign * 46, hip_y + 6)
            ctx.line_to(sign * 14, hip_y + 6)
            ctx.close_path()
            set_color(ctx, white, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.5)
            ctx.stroke()

    elif arch == "7_engineer" or high_vis_vest:
        # High-visibility yellow/orange vest (matches both #7 and the gas station attendants in screenshot!)
        if high_vis_vest:
            draw_bean_torso_path(ctx, 0, torso_cy, rx=48, ry=54)
            set_color(ctx, pal["yellow"], alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.5)
            ctx.stroke()
        ctx.move_to(-18, shoulder_y + 3)
        ctx.line_to(0, shoulder_y + 36)
        ctx.line_to(18, shoulder_y + 3)
        ctx.close_path()
        set_color(ctx, ink, alpha)
        ctx.fill()
        set_color(ctx, pal["red"] if high_vis_vest else white, alpha)
        ctx.set_line_width(8.0)
        ctx.move_to(-24, shoulder_y + 10)
        ctx.line_to(-24, torso_cy + 15)
        ctx.move_to(24, shoulder_y + 10)
        ctx.line_to(24, torso_cy + 15)
        ctx.move_to(-45, torso_cy + 12)
        ctx.line_to(45, torso_cy + 12)
        ctx.stroke()

    elif arch == "8_superhero":
        draw_star(ctx, 0, torso_cy - 6, 20, 9)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.5)
        ctx.stroke()
        ctx.arc(0, torso_cy, 49, 0.22 * math.pi, 0.78 * math.pi)
        ctx.close_path()
        set_color(ctx, ink, alpha)
        ctx.fill()

    elif arch == "9_artist":
        # Scarf around neck
        draw_rounded_rect(ctx, -34, shoulder_y - 2, 68, 18, 8)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.0)
        ctx.stroke()
        draw_rounded_rect(ctx, 12, shoulder_y + 12, 18, 46, 4)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()

    elif arch == "10_astronaut":
        draw_rounded_rect(ctx, -22, torso_cy - 20, 44, 28, 6)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.5)
        ctx.stroke()

    elif arch == "11_ninja":
        # Crossed ninja gi sash & belt
        ctx.set_line_width(5.5)
        set_color(ctx, white, alpha * 0.25)
        ctx.move_to(-28, shoulder_y + 8)
        ctx.line_to(28, torso_cy + 10)
        ctx.stroke()
        draw_rounded_rect(ctx, -46, torso_cy + 6, 92, 18, 6)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()

    elif arch in ("12_cowboy", "18_rockstar", "28_explorer", "29_punk"):
        # Open vest panels over white shirt
        for sign in (-1.0, 1.0):
            ctx.move_to(sign * 14, shoulder_y + 6)
            ctx.curve_to(sign * 46, shoulder_y + 12, sign * 52, torso_cy, sign * 42, hip_y)
            ctx.line_to(sign * 14, hip_y)
            ctx.close_path()
            set_color(ctx, mid, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.5)
            ctx.stroke()
        if arch == "18_rockstar":
            # Electric Guitar slung diagonally across torso!
            ctx.save()
            ctx.translate(-8, torso_cy + 16)
            ctx.rotate(-0.45)
            ctx.arc(-15, 0, 26, 0, 2 * math.pi)
            ctx.arc(15, 0, 22, 0, 2 * math.pi)
            set_color(ctx, mid, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.5)
            ctx.stroke()
            draw_rounded_rect(ctx, 25, -7, 78, 14, 4)
            set_color(ctx, ink, alpha)
            ctx.fill()
            ctx.restore()

    elif arch == "13_pirate":
        ctx.arc(0, torso_cy, 49, 0.15 * math.pi, 0.85 * math.pi)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        draw_rounded_rect(ctx, -11, torso_cy + 14, 22, 18, 3)
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.5)
        ctx.stroke()

    elif arch == "14_king":
        ctx.set_line_width(11.0)
        set_color(ctx, white, alpha)
        ctx.move_to(-16, shoulder_y + 10)
        ctx.line_to(-32, hip_y + 6)
        ctx.move_to(16, shoulder_y + 10)
        ctx.line_to(32, hip_y + 6)
        ctx.stroke()
        for cx_f, cy_f in [(-34, shoulder_y + 6), (-18, shoulder_y + 12), (18, shoulder_y + 12), (34, shoulder_y + 6)]:
            ctx.arc(cx_f, cy_f, 13, 0, 2 * math.pi)
            set_color(ctx, white, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(4.5)
            ctx.stroke()

    elif arch == "15_firefighter":
        set_color(ctx, white, alpha)
        ctx.set_line_width(9.0)
        ctx.move_to(-46, torso_cy - 6)
        ctx.line_to(46, torso_cy - 6)
        ctx.move_to(-44, torso_cy + 22)
        ctx.line_to(44, torso_cy + 22)
        ctx.stroke()

    elif arch == "16_farmer":
        draw_rounded_rect(ctx, -32, torso_cy - 22, 64, 68, 12)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        ctx.set_line_width(9.0)
        ctx.move_to(-22, shoulder_y + 4)
        ctx.line_to(-22, torso_cy - 18)
        ctx.move_to(22, shoulder_y + 4)
        ctx.line_to(22, torso_cy - 18)
        ctx.stroke()

    elif arch == "17_police":
        # Tie + Police Shield Badge + Utility Belt
        ctx.move_to(0, shoulder_y + 8)
        ctx.line_to(-7, torso_cy + 8)
        ctx.line_to(0, torso_cy + 16)
        ctx.line_to(7, torso_cy + 8)
        ctx.close_path()
        set_color(ctx, ink, alpha)
        ctx.fill()
        ctx.arc(20, torso_cy - 12, 9, 0, 2 * math.pi)
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(3.5)
        ctx.stroke()

    elif arch == "20_clown":
        # Polka dots + Giant Bow Tie
        for dx, dy in [(-20, -10), (20, -12), (0, 8), (-18, 22), (18, 20)]:
            ctx.arc(dx, torso_cy + dy, 7.5, 0, 2 * math.pi)
            set_color(ctx, mid, alpha)
            ctx.fill()
        ctx.move_to(0, shoulder_y + 6)
        ctx.line_to(-28, shoulder_y - 8)
        ctx.line_to(-28, shoulder_y + 20)
        ctx.line_to(28, shoulder_y - 8)
        ctx.line_to(28, shoulder_y + 20)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.0)
        ctx.stroke()

    elif arch == "23_boxer":
        # Championship belt & trunks
        draw_rounded_rect(ctx, -45, torso_cy + 8, 90, 42, 8)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        ctx.arc(0, torso_cy + 16, 15, 0, 2 * math.pi)
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()

    elif arch == "26_viking":
        # Round Viking Shield on right side
        ctx.arc(46, torso_cy + 12, 34, 0, 2 * math.pi)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.0)
        ctx.stroke()
        ctx.arc(46, torso_cy + 12, 11, 0, 2 * math.pi)
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()

    elif arch == "27_football":
        # Wide football shoulder pads + "99"
        draw_rounded_rect(ctx, -64, shoulder_y - 2, 128, 38, 18)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.0)
        ctx.stroke()
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(34.0)
        set_color(ctx, white, alpha)
        ext = ctx.text_extents("99")
        ctx.move_to(-ext.width / 2, torso_cy + 18)
        ctx.show_text("99")

    elif arch == "30_knight":
        for sign in (-1.0, 1.0):
            ctx.arc(sign * 42, shoulder_y + 14, 18, 0, 2 * math.pi)
            set_color(ctx, mid, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.5)
            ctx.stroke()
        ctx.move_to(-32, shoulder_y + 12)
        ctx.line_to(0, torso_cy - 8)
        ctx.line_to(32, shoulder_y + 12)
        ctx.move_to(-46, torso_cy + 20)
        ctx.line_to(46, torso_cy + 20)
        ctx.stroke()
        ctx.save()
        ctx.translate(36, torso_cy + 18)
        ctx.rotate(-0.55)
        draw_rounded_rect(ctx, -6, 0, 12, 68, 4)
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.5)
        ctx.stroke()
        ctx.move_to(-18, 0)
        ctx.line_to(18, 0)
        ctx.set_line_width(6.5)
        ctx.stroke()
        ctx.restore()

    elif arch in ("31_student", "34_courier"):
        # Backpack straps over shoulders
        ctx.set_line_width(10.0)
        set_color(ctx, white, alpha)
        ctx.move_to(-28, shoulder_y + 4)
        ctx.curve_to(-34, torso_cy - 10, -34, torso_cy + 10, -28, torso_cy + 24)
        ctx.move_to(28, shoulder_y + 4)
        ctx.curve_to(34, torso_cy - 10, 34, torso_cy + 10, 28, torso_cy + 24)
        ctx.stroke()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.5)
        ctx.move_to(0, shoulder_y + 6)
        ctx.line_to(0, hip_y)
        ctx.stroke()

    elif arch == "32_businessman":
        # Classic dark tie + belt & slacks on lower half
        ctx.move_to(0, shoulder_y + 6)
        ctx.line_to(-9, torso_cy + 4)
        ctx.line_to(0, torso_cy + 16)
        ctx.line_to(9, torso_cy + 4)
        ctx.close_path()
        set_color(ctx, ink, alpha)
        ctx.fill()
        ctx.arc(0, torso_cy, 49, 0.15 * math.pi, 0.85 * math.pi)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()

    elif arch in ("35_professor", "38_waiter", "40_grandpa"):
        # V-neck shirt collar + vest/jacket buttons
        ctx.move_to(-16, shoulder_y + 3)
        ctx.line_to(0, shoulder_y + 32)
        ctx.line_to(16, shoulder_y + 3)
        ctx.close_path()
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.5)
        ctx.stroke()
        ctx.move_to(0, shoulder_y + 32)
        ctx.line_to(0, hip_y)
        ctx.stroke()
        if arch == "38_waiter":
            # Bow tie
            ctx.move_to(0, shoulder_y + 14)
            ctx.line_to(-14, shoulder_y + 6)
            ctx.line_to(-14, shoulder_y + 22)
            ctx.line_to(14, shoulder_y + 6)
            ctx.line_to(14, shoulder_y + 22)
            ctx.close_path()
            set_color(ctx, mid, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(3.5)
            ctx.stroke()

    elif arch == "36_tourist":
        # Camera hanging on neck strap + shorts
        ctx.set_line_width(4.5)
        set_color(ctx, ink, alpha)
        ctx.move_to(-18, shoulder_y + 4)
        ctx.line_to(-14, torso_cy - 6)
        ctx.move_to(18, shoulder_y + 4)
        ctx.line_to(14, torso_cy - 6)
        ctx.stroke()
        draw_rounded_rect(ctx, -20, torso_cy - 10, 40, 28, 6)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()
        ctx.arc(0, torso_cy + 4, 8, 0, 2 * math.pi)
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()

    elif arch == "37_runner":
        # Athletic shorts at bottom of bean
        ctx.arc(0, torso_cy, 49, 0.18 * math.pi, 0.82 * math.pi)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()

    ctx.restore()

    # ------------------------------------------------------------------
    # 3. CURVED BÉZIER ARMS, FORK HANDS & HANDHELD PROPS
    # ------------------------------------------------------------------
    sh_lx, sh_ly = -42.0, shoulder_y + 14.0
    sh_rx, sh_ry = 42.0, shoulder_y + 14.0
    sway = math.sin(t * 3.0 + seed) * 3.5
    wave_osc = math.sin(t * 8.5 + seed) * 10.0

    esquerdo, direito = postura_bracos(pose, shoulder_y, torso_cy, hip_y, sway, wave_osc, walk_phase)
    if pose_anterior is not None and peso_pose < 1:
        ant_l, ant_r = postura_bracos(pose_anterior, shoulder_y, torso_cy, hip_y, sway, wave_osc, walk_phase)
        esquerdo = interpolar_braco(ant_l, esquerdo, peso_pose)
        direito = interpolar_braco(ant_r, direito, peso_pose)
    el_lx, el_ly, ha_lx, ha_ly, ang_l = contato_braco(esquerdo, (sh_lx, sh_ly), ik_hand_l, peso_ik_l, -1)
    el_rx, el_ry, ha_rx, ha_ry, ang_r = contato_braco(direito, (sh_rx, sh_ry), ik_hand_r, peso_ik_r, 1)

    hand_type = "boxer_glove" if arch == "23_boxer" else ("mitten" if arch in ("10_astronaut", "30_knight") else "fork")
    ctx.set_line_width(7.0)
    set_color(ctx, ink, alpha)

    ctx.move_to(sh_lx, sh_ly)
    ctx.curve_to(el_lx, el_ly, el_lx, el_ly, ha_lx, ha_ly)
    ctx.stroke()
    draw_fork_hand(ctx, ha_lx, ha_ly, ang_l, ink, alpha, hand_style=hand_type, fill_col=mid)
    draw_handheld_prop(ctx, ha_lx, ha_ly, prop_l, pal, alpha)

    ctx.move_to(sh_rx, sh_ry)
    ctx.curve_to(el_rx, el_ry, el_rx, el_ry, ha_rx, ha_ry)
    ctx.stroke()
    draw_fork_hand(ctx, ha_rx, ha_ry, ang_r, ink, alpha, hand_style=hand_type, fill_col=mid)
    draw_handheld_prop(ctx, ha_rx, ha_ry, prop_r, pal, alpha)

    # ------------------------------------------------------------------
    # 4. MOUTHLESS EXPRESSIVE HEAD & ARCHETYPE HEADGEAR (#1 to #30)
    # ------------------------------------------------------------------
    head_tilt = math.sin(t * 2.3 + seed) * 0.04
    ctx.save()
    ctx.translate(0.0, head_cy)
    ctx.rotate(head_tilt)

    # Full-helmet special heads (#10 Astronaut, #21 Diver)
    if arch == "10_astronaut":
        for sign in (-1.0, 1.0):
            draw_rounded_rect(ctx, sign * 48 - 8, -14, 16, 28, 6)
            set_color(ctx, mid, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.5)
            ctx.stroke()
        ctx.arc(0, 0, 52.0, 0, 2 * math.pi)
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.5)
        ctx.stroke()
        ctx.arc(0, 0, 38.0, 0, 2 * math.pi)
        set_color(ctx, ink, alpha)
        ctx.fill()
        set_color(ctx, white, alpha)
        ctx.set_line_width(5.5)
        ctx.arc(0, 0, 27.0, math.pi * 1.12, math.pi * 1.42)
        ctx.stroke()
        ctx.restore()
        ctx.restore()
        return

    # Base Circular Head
    ctx.save()
    ctx.scale(1.04, 0.98)
    ctx.arc(0, 0, head_r, 0, 2 * math.pi)
    ctx.restore()
    set_color(ctx, mid if arch == "21_diver" else white, alpha)
    ctx.fill_preserve()
    set_color(ctx, ink, alpha)
    ctx.set_line_width(6.5)
    ctx.stroke()

    if arch == "21_diver":
        # Inner porthole face window for Diver (#21)
        ctx.arc(0, 0, 26.0, 0, 2 * math.pi)
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()

    # Eyes & Eyebrows (MOUTHLESS ACTING!)
    gx, gy = look_dir
    eye_lx, eye_ly = -13.0 + gx, -6.0 + gy
    eye_rx, eye_ry = 13.0 + gx, -6.0 + gy
    blink_mod = (t + seed) % 3.2
    is_blinking = 0.0 <= blink_mod <= 0.11

    set_color(ctx, ink, alpha)
    if is_blinking or expression == "happy_eyes":
        ctx.set_line_width(4.2)
        ctx.arc(eye_lx, eye_ly + 3, 5.5, math.pi * 1.1, math.pi * 1.9)
        ctx.stroke()
        if arch != "13_pirate":
            ctx.arc(eye_rx, eye_ry + 3, 5.5, math.pi * 1.1, math.pi * 1.9)
            ctx.stroke()
    else:
        ctx.arc(eye_lx, eye_ly, 4.8, 0, 2 * math.pi)
        ctx.fill()
        if arch != "13_pirate":
            ctx.arc(eye_rx, eye_ry, 4.8, 0, 2 * math.pi)
            ctx.fill()

    # Pirate Eye Patch (#13)
    if arch == "13_pirate":
        ctx.arc(eye_rx, eye_ry, 10.0, 0, 2 * math.pi)
        set_color(ctx, ink, alpha)
        ctx.fill()
        ctx.set_line_width(4.5)
        ctx.move_to(-38, -22)
        ctx.line_to(40, -2)
        ctx.stroke()

    # Round Glasses (#6 Scientist, #35 Professor, #40 Grandpa) or Dark Sunglasses (#25 Agent)
    if arch in ("6_scientist", "35_professor", "40_grandpa"):
        ctx.set_line_width(4.2)
        ctx.arc(eye_lx, eye_ly, 11.5, 0, 2 * math.pi)
        ctx.stroke()
        ctx.arc(eye_rx, eye_ry, 11.5, 0, 2 * math.pi)
        ctx.stroke()
        ctx.move_to(eye_lx + 11.5, eye_ly)
        ctx.line_to(eye_rx - 11.5, eye_ry)
        ctx.stroke()
    elif arch == "25_agent":
        draw_rounded_rect(ctx, -30, -16, 26, 18, 5)
        draw_rounded_rect(ctx, 4, -16, 26, 18, 5)
        set_color(ctx, ink, alpha)
        ctx.fill()
        ctx.set_line_width(4.5)
        ctx.move_to(-38, -10)
        ctx.line_to(38, -10)
        ctx.stroke()

    # Superhero Domino Mask (#8)
    if arch == "8_superhero":
        draw_rounded_rect(ctx, -40, -19, 80, 24, 11)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.0)
        ctx.stroke()
        for ex_m in (eye_lx, eye_rx):
            ctx.arc(ex_m, eye_ly, 8.5, 0, 2 * math.pi)
            set_color(ctx, white, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(3.5)
            ctx.stroke()
            ctx.arc(ex_m, eye_ly, 4.2, 0, 2 * math.pi)
            ctx.fill()

    # Eyebrows
    ctx.set_line_width(4.2)
    set_color(ctx, ink, alpha)
    brow_y = -18.0 + math.sin(t * 4.5 + seed) * 1.5
    if expression in ("determined", "focused"):
        ctx.move_to(eye_lx - 7, brow_y - 3)
        ctx.line_to(eye_lx + 6, brow_y + 2)
        ctx.move_to(eye_rx - 6, brow_y + 2)
        ctx.line_to(eye_rx + 7, brow_y - 3)
    elif expression == "sad":
        ctx.move_to(eye_lx - 7, brow_y + 2)
        ctx.line_to(eye_lx + 6, brow_y - 3)
        ctx.move_to(eye_rx - 6, brow_y - 3)
        ctx.line_to(eye_rx + 7, brow_y + 2)
    else:
        ctx.move_to(eye_lx - 6, brow_y)
        ctx.curve_to(eye_lx, brow_y - 4, eye_lx, brow_y - 4, eye_lx + 6, brow_y)
        ctx.move_to(eye_rx - 6, brow_y)
        ctx.curve_to(eye_rx, brow_y - 4, eye_rx, brow_y - 4, eye_rx + 6, brow_y)
    ctx.stroke()

    # Minimal Nose Tick (or Clown Round Nose #20) — NO MOUTH LINE!
    if arch == "20_clown":
        ctx.arc(0, 4, 10, 0, 2 * math.pi)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(4.0)
        ctx.stroke()
    else:
        ctx.set_line_width(3.5)
        ctx.move_to(2.0 + gx * 0.4, 1.0 + gy * 0.4)
        ctx.line_to(4.5 + gx * 0.4, 7.0 + gy * 0.4)
        ctx.line_to(0.0 + gx * 0.4, 7.5 + gy * 0.4)
        ctx.stroke()

    # Mustache for #3 Detective (No mouth opening underneath!)
    if arch == "3_detective":
        ctx.move_to(0, 15)
        ctx.curve_to(-10, 10, -22, 15, -24, 22)
        ctx.curve_to(-14, 24, -6, 20, 0, 18)
        ctx.curve_to(6, 20, 14, 24, 24, 22)
        ctx.curve_to(22, 15, 10, 10, 0, 15)
        ctx.close_path()
        set_color(ctx, ink, alpha)
        ctx.fill()

    # ------------------------------------------------------------------
    # 5. HEADGEAR / HAIR / HELMETS FOR ALL 40 ARCHETYPES
    # ------------------------------------------------------------------
    if arch in ("classic_narrator", "32_businessman", "33_barista", "38_waiter", "39_shopper"):
        # Swept hair from original video narrator & civilian archetypes (#32, #33, #38, #39)
        set_color(ctx, ink, alpha)
        ctx.move_to(-43, -6)
        ctx.curve_to(-48, -42, -12, -58, 22, -50)
        ctx.curve_to(38, -46, 46, -34, 50, -24)
        ctx.line_to(34, -24)
        ctx.curve_to(43, -16, 46, -8, 43, 0)
        ctx.curve_to(34, -18, 16, -24, -24, -26)
        ctx.curve_to(-22, -14, -25, -4, -30, 4)
        ctx.close_path()
        ctx.fill()

    elif arch in ("31_student", "34_courier"):
        # Baseball cap (backwards for #31 Student, forwards for #34 Courier)
        ctx.arc(0, -18, 45.0, math.pi * 1.02, math.pi * 1.98)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.0)
        ctx.stroke()
        v_sign = -1.0 if arch == "31_student" else 1.0
        ctx.move_to(v_sign * 5, -22)
        ctx.curve_to(v_sign * 35, -34, v_sign * 62, -32, v_sign * 68, -24)
        ctx.curve_to(v_sign * 55, -16, v_sign * 25, -16, v_sign * 5, -22)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()

    elif arch in ("35_professor", "40_grandpa"):
        # Fluffy side hair tufts on bald dome (#35 Professor & #40 Grandpa)
        for sign in (-1.0, 1.0):
            ctx.arc(sign * 45, -12, 14, 0, 2 * math.pi)
            set_color(ctx, white, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.0)
            ctx.stroke()

    elif arch == "1_cap_gamer":
        for sign in (-1.0, 1.0):
            draw_rounded_rect(ctx, sign * 46 - 9, -18, 18, 34, 8)
            set_color(ctx, white, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.5)
            ctx.stroke()
        ctx.arc(0, -18, 45.0, math.pi * 1.02, math.pi * 1.98)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.0)
        ctx.stroke()
        ctx.move_to(5, -22)
        ctx.curve_to(35, -34, 62, -32, 68, -24)
        ctx.curve_to(55, -16, 25, -16, 5, -22)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()

    elif arch == "2_chef":
        ctx.move_to(-28, -36)
        ctx.line_to(-32, -62)
        ctx.curve_to(-52, -66, -48, -98, -22, -96)
        ctx.curve_to(-12, -116, 12, -116, 22, -96)
        ctx.curve_to(48, -98, 52, -66, 32, -62)
        ctx.line_to(28, -36)
        ctx.close_path()
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.0)
        ctx.stroke()

    elif arch in ("3_detective", "12_cowboy", "25_agent", "28_explorer"):
        ctx.move_to(-34, -32)
        ctx.line_to(-24, -68)
        ctx.curve_to(-8, -74, 0, -62, 12, -72)
        ctx.line_to(26, -66)
        ctx.line_to(34, -32)
        ctx.close_path()
        set_color(ctx, white if arch == "28_explorer" else mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.0)
        ctx.stroke()
        ctx.save()
        ctx.translate(0, -32)
        ctx.scale(1.0, 0.18)
        ctx.arc(0, 0, 62, 0, 2 * math.pi)
        ctx.restore()
        set_color(ctx, white if arch == "28_explorer" else mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()

    elif arch in ("4_athlete", "37_runner"):
        draw_rounded_rect(ctx, -45, -34, 90, 14, 5)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()

    elif arch == "5_wizard":
        # Long flowing white beard (NO mouth line inside beard!)
        ctx.move_to(-38, 8)
        ctx.curve_to(-44, 45, -18, 75, 0, 96)
        ctx.curve_to(18, 75, 44, 45, 38, 8)
        ctx.curve_to(22, 18, -22, 18, -38, 8)
        ctx.close_path()
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        ctx.move_to(-40, -34)
        ctx.line_to(4, -122)
        ctx.line_to(32, -104)
        ctx.line_to(14, -96)
        ctx.line_to(40, -34)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.0)
        ctx.stroke()
        ctx.save()
        ctx.translate(0, -34)
        ctx.scale(1.0, 0.22)
        ctx.arc(0, 0, 68, 0, 2 * math.pi)
        ctx.restore()
        set_color(ctx, ink, alpha)
        ctx.fill()
        for sx, sy, sr in [(-4, -84, 9), (-14, -56, 8), (14, -60, 10)]:
            draw_star(ctx, sx, sy, sr, sr * 0.45)
            set_color(ctx, white, alpha)
            ctx.fill()

    elif arch in ("6_scientist", "18_rockstar"):
        ctx.move_to(-42, -12)
        for px, py in [
            (-58, -22), (-46, -34), (-56, -48), (-36, -52), (-42, -68),
            (-16, -58), (0, -72), (16, -56), (38, -68), (34, -50),
            (56, -48), (44, -32), (56, -20), (42, -10),
        ]:
            ctx.line_to(px, py)
        ctx.curve_to(25, -34, -25, -34, -42, -12)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()

    elif arch in ("7_engineer", "15_firefighter"):
        if high_vis_vest:
            # Dark Baseball Cap for Gas Station Attendant (exact match to screenshot!)
            set_color(ctx, ink, alpha)
            ctx.arc(0, -20, 43.0, math.pi, 2 * math.pi)
            ctx.close_path()
            ctx.fill()
            ctx.move_to(5, -24)
            ctx.curve_to(35, -32, 58, -28, 62, -20)
            ctx.curve_to(45, -14, 20, -16, 5, -24)
            ctx.close_path()
            ctx.fill()
        else:
            ctx.arc(0, -24, 44.0, math.pi, 2 * math.pi)
            ctx.close_path()
            set_color(ctx, mid if arch == "15_firefighter" else white, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(6.0)
            ctx.stroke()
            draw_rounded_rect(ctx, -50, -30, 100, 12, 6)
            ctx.fill_preserve()
            ctx.stroke()

    elif arch == "9_artist":
        ctx.save()
        ctx.translate(-4, -42)
        ctx.rotate(0.15)
        ctx.scale(1.4, 0.55)
        ctx.arc(0, 0, 36, 0, 2 * math.pi)
        ctx.restore()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()

    elif arch == "11_ninja":
        # Ninja face mask covering lower face + head hood
        ctx.arc(0, 0, head_r, 0.05 * math.pi, 0.95 * math.pi)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        ctx.arc(0, 0, head_r, 1.08 * math.pi, 1.92 * math.pi)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()

    elif arch == "13_pirate":
        # Full mouthless beard + Skull Pirate Hat
        ctx.move_to(-40, 6)
        ctx.line_to(-34, 42)
        ctx.line_to(0, 58)
        ctx.line_to(34, 42)
        ctx.line_to(40, 6)
        ctx.curve_to(20, 16, -20, 16, -40, 6)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        ctx.move_to(-66, -42)
        ctx.curve_to(-45, -42, -35, -86, 0, -86)
        ctx.curve_to(35, -86, 45, -42, 66, -42)
        ctx.curve_to(56, -24, -56, -24, -66, -42)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.0)
        ctx.stroke()
        ctx.arc(0, -58, 12, 0, 2 * math.pi)
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(3.5)
        ctx.stroke()

    elif arch == "14_king":
        # Full mouthless royal beard + Jeweled Crown
        ctx.move_to(-40, 6)
        ctx.curve_to(-42, 34, -22, 48, 0, 52)
        ctx.curve_to(22, 48, 42, 34, 40, 6)
        ctx.curve_to(22, 16, -22, 16, -40, 6)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        ctx.move_to(-36, -34)
        ctx.line_to(-44, -72)
        ctx.line_to(-22, -54)
        ctx.line_to(0, -80)
        ctx.line_to(22, -54)
        ctx.line_to(44, -72)
        ctx.line_to(36, -34)
        ctx.close_path()
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()

    elif arch in ("16_farmer", "36_tourist"):
        ctx.arc(0, -32, 36.0, math.pi, 2 * math.pi)
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        ctx.save()
        ctx.translate(0, -30)
        ctx.scale(1.0, 0.20)
        ctx.arc(0, 0, 72, 0, 2 * math.pi)
        ctx.restore()
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()

    elif arch == "17_police":
        ctx.move_to(-38, -32)
        ctx.line_to(-46, -54)
        ctx.line_to(0, -68)
        ctx.line_to(46, -54)
        ctx.line_to(38, -32)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()

    elif arch == "19_samurai":
        ctx.arc(0, -56, 14, 0, 2 * math.pi)
        set_color(ctx, ink, alpha)
        ctx.fill()

    elif arch == "20_clown":
        for sign in (-1.0, 1.0):
            ctx.arc(sign * 52, -24, 22, 0, 2 * math.pi)
            set_color(ctx, mid, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.set_line_width(5.5)
            ctx.stroke()

    elif arch == "24_aviator":
        ctx.arc(0, -14, 47, math.pi * 0.9, math.pi * 2.1)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        for gx_a in (-16, 16):
            ctx.arc(gx_a, -32, 11, 0, 2 * math.pi)
            set_color(ctx, white, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.stroke()

    elif arch == "26_viking":
        # Full Viking Beard + Horned Helmet
        ctx.move_to(-40, 6)
        ctx.line_to(-28, 52)
        ctx.line_to(0, 68)
        ctx.line_to(28, 52)
        ctx.line_to(40, 6)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        for sign in (-1.0, 1.0):
            ctx.move_to(sign * 36, -34)
            ctx.curve_to(sign * 65, -42, sign * 65, -68, sign * 48, -78)
            ctx.curve_to(sign * 48, -58, sign * 42, -46, sign * 28, -42)
            ctx.close_path()
            set_color(ctx, white, alpha)
            ctx.fill_preserve()
            set_color(ctx, ink, alpha)
            ctx.stroke()
        ctx.arc(0, -28, 42, math.pi, 2 * math.pi)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()

    elif arch == "27_football":
        ctx.arc(0, -4, 48, math.pi * 0.85, math.pi * 2.15)
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(6.0)
        ctx.stroke()
        # Facemask cage bars
        ctx.set_line_width(4.5)
        ctx.move_to(-32, 10)
        ctx.line_to(32, 10)
        ctx.move_to(-28, 22)
        ctx.line_to(28, 22)
        ctx.stroke()

    elif arch == "29_punk":
        ctx.move_to(-12, -42)
        ctx.line_to(-18, -78)
        ctx.line_to(-4, -64)
        ctx.line_to(0, -86)
        ctx.line_to(8, -64)
        ctx.line_to(20, -76)
        ctx.line_to(12, -42)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()

    elif arch == "30_knight":
        ctx.move_to(0, -45)
        ctx.curve_to(10, -82, 46, -78, 56, -56)
        ctx.curve_to(38, -44, 18, -52, 0, -45)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.set_line_width(5.5)
        ctx.stroke()
        ctx.arc(0, -8, 46.0, math.pi * 1.05, math.pi * 1.95)
        ctx.line_to(38, -8)
        ctx.line_to(0, -18)
        ctx.line_to(-38, -8)
        ctx.close_path()
        set_color(ctx, mid, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()
        ctx.move_to(-44, 4)
        ctx.line_to(0, 12)
        ctx.line_to(44, 4)
        ctx.curve_to(40, 34, 22, 46, 0, 48)
        ctx.curve_to(-22, 46, -40, 34, -44, 4)
        ctx.close_path()
        set_color(ctx, white, alpha)
        ctx.fill_preserve()
        set_color(ctx, ink, alpha)
        ctx.stroke()
        ctx.set_line_width(4.0)
        for vx in (-22, -11, 0, 11, 22):
            ctx.move_to(vx, 15)
            ctx.line_to(vx, 34)
        ctx.stroke()

    ctx.restore()
    ctx.restore()
