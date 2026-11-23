#!/usr/bin/env python3
"""
stickman_engine.py — Master 60 FPS Vector Animation Director & Video Renderer (Super-Skill v3)
Combines:
1. All 30 Mouthless Bean-Body Archetypes (puppet_30.py) — zero lip-sync, pure expressive acting.
2. Dual-World Color Architecture (Cream Concept World #F5EDD6 vs. Kraft Storyboard World #C7B59C).
3. Foreground Narrator Overlay (Picture-in-Picture host looking into background scenes, matching user's screenshot).
4. Rich Vector Environments, Furniture & Moving Vehicles (scenes_and_props.py: 7-segment LCD Gas Station,
   Detailed Sage-Green Sedan with driver & 6-spoke wheels, Glass Office Lobby with plants & bench,
   3D Books, Smartphone Feeds with Magnifier, Puzzle Grids, Vault Shield, FII Buildings, Money Mountains).
5. Virtual 2D Camera Choreography (Camera2D: MCU Hooks, Elastic Pull-backs, Whip-Pans, Binocular Masks, 3D Board Wipes).
"""

import os
import sys
import math
import json
import wave
import struct
import random
import subprocess
import cairo

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from puppet_30 import (
    PALETTE_CREAM,
    PALETTE_KRAFT,
    clamp,
    set_color,
    draw_rounded_rect,
    draw_puppet_30,
)
from scenes_and_props import (
    lerp,
    create_paper_background,
    draw_foreground_narrator,
    draw_detailed_gas_station,
    draw_detailed_sedan_car,
    draw_office_lobby_environment,
    draw_3d_book,
    draw_smartphone_feed,
    draw_puzzle_grid_2x2,
    draw_kraft_board_wipe,
    draw_binocular_mask,
)

# ==============================================================================
# 1. MATHEMATICAL EASING & CAMERA CHOREOGRAPHY
# ==============================================================================

def prog(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / (t1 - t0), 0.0, 1.0)

def ease_out_cubic(u):
    u = clamp(u)
    return 1.0 - (1.0 - u) ** 3

def ease_in_out_cubic(u):
    u = clamp(u)
    return 4.0 * u * u * u if u < 0.5 else 1.0 - ((-2.0 * u + 2.0) ** 3) / 2.0

def ease_out_back(u, overshoot=1.70158):
    u = clamp(u)
    if u == 0.0 or u == 1.0:
        return u
    c3 = overshoot + 1.0
    return 1.0 + c3 * ((u - 1.0) ** 3) + overshoot * ((u - 1.0) ** 2)

def ease_out_bounce(u):
    u = clamp(u)
    n1 = 7.5625
    d1 = 2.75
    if u < 1.0 / d1:
        return n1 * u * u
    elif u < 2.0 / d1:
        u -= 1.5 / d1
        return n1 * u * u + 0.75
    elif u < 2.5 / d1:
        u -= 2.25 / d1
        return n1 * u * u + 0.9375
    else:
        u -= 2.625 / d1
        return n1 * u * u + 0.984375

class Camera2D:
    def __init__(self):
        self.keyframes = []

    def add_shot(self, t0, t1, cx0, cy0, z0, cx1, cy1, z1, ease_fn=ease_in_out_cubic, rot0=0.0, rot1=0.0):
        self.keyframes.append((t0, t1, cx0, cy0, z0, cx1, cy1, z1, ease_fn, rot0, rot1))

    def evaluate(self, t):
        cx, cy, z, rot = 960.0, 540.0, 1.0, 0.0
        for (t0, t1, cx0, cy0, z0, cx1, cy1, z1, ease_fn, rot0, rot1) in self.keyframes:
            if t >= t0:
                u = ease_fn(prog(t, t0, t1))
                cx = lerp(cx0, cx1, u)
                cy = lerp(cy0, cy1, u)
                z = lerp(z0, z1, u)
                rot = lerp(rot0, rot1, u)
        return cx, cy, z, rot

    def apply(self, ctx, t, shake_amp=0.0):
        cx, cy, z, rot = self.evaluate(t)
        if shake_amp > 0.0:
            cx += math.sin(t * 58.0) * shake_amp
            cy += math.cos(t * 73.0) * shake_amp
        ctx.translate(960.0, 540.0)
        if abs(rot) > 1e-5:
            ctx.rotate(rot)
        ctx.scale(z, z)
        ctx.translate(-cx, -cy)

# ==============================================================================
# 2. ADDITIONAL INVESTING & STORYTELLING PROPS
# ==============================================================================

def draw_curved_banner_text(ctx, text, cx, cy, radius, progress=1.0, color=PALETTE_CREAM["ink"], font_size=30.0):
    if progress <= 0.01:
        return
    ctx.save()
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(font_size)
    set_color(ctx, color)

    n = len(text)
    visible_n = max(1, int(math.ceil(n * clamp(progress))))
    angle_step = 0.11
    total_ang = (n - 1) * angle_step
    start_ang = -math.pi / 2.0 - total_ang / 2.0

    for i in range(visible_n):
        ch = text[i]
        ang = start_ang + i * angle_step
        px = cx + math.cos(ang) * radius
        py = cy + math.sin(ang) * radius
        ctx.save()
        ctx.translate(px, py)
        ctx.rotate(ang + math.pi / 2.0)
        ext = ctx.text_extents(ch)
        ctx.move_to(-ext.width / 2.0, 0)
        ctx.show_text(ch)
        ctx.restore()
    ctx.restore()

def draw_badge_card(ctx, x, y, w, h, title, subtitle, scale=1.0, accent=PALETTE_CREAM["mid"], ink=PALETTE_CREAM["ink"]):
    if scale <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)
    draw_rounded_rect(ctx, -w / 2, -h / 2, w, h, 18)
    set_color(ctx, PALETTE_CREAM["white"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(6.0)
    ctx.stroke()

    draw_rounded_rect(ctx, -w / 2 + 8, -h / 2 + 8, w - 16, 48, 12)
    set_color(ctx, accent)
    ctx.fill()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(24.0)
    set_color(ctx, PALETTE_CREAM["white"])
    ext = ctx.text_extents(title)
    ctx.move_to(-ext.width / 2, -h / 2 + 41)
    ctx.show_text(title)

    ctx.set_font_size(30.0)
    set_color(ctx, ink)
    ext2 = ctx.text_extents(subtitle)
    ctx.move_to(-ext2.width / 2, 26)
    ctx.show_text(subtitle)
    ctx.restore()

def draw_vault_shield(ctx, x, y, scale=1.0, t=0.0):
    if scale <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)
    ink = PALETTE_CREAM["ink"]

    ctx.move_to(0, -145)
    ctx.line_to(115, -105)
    ctx.curve_to(115, 15, 75, 95, 0, 145)
    ctx.curve_to(-75, 95, -115, 15, -115, -105)
    ctx.close_path()
    set_color(ctx, PALETTE_CREAM["mid"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(7.0)
    ctx.stroke()

    ctx.move_to(0, -122)
    ctx.line_to(94, -88)
    ctx.curve_to(94, 8, 60, 75, 0, 118)
    ctx.curve_to(-60, 75, -94, 8, -94, -88)
    ctx.close_path()
    set_color(ctx, PALETTE_CREAM["white"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(5.0)
    ctx.stroke()

    ctx.save()
    ctx.translate(0, -12)
    ctx.rotate(t * 0.8)
    ctx.arc(0, 0, 42, 0, 2 * math.pi)
    set_color(ctx, PALETTE_CREAM["gold"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(5.5)
    ctx.stroke()
    for k in range(6):
        ang = k * math.pi / 3.0
        ctx.move_to(0, 0)
        ctx.line_to(math.cos(ang) * 42, math.sin(ang) * 42)
    ctx.stroke()
    ctx.arc(0, 0, 14, 0, 2 * math.pi)
    set_color(ctx, ink)
    ctx.fill()
    ctx.restore()
    ctx.restore()

def draw_fii_building(ctx, x, y, w, h, label, scale=1.0, accent=PALETTE_CREAM["mid"]):
    if scale <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)
    ink = PALETTE_CREAM["ink"]

    draw_rounded_rect(ctx, -w / 2, -h, w, h, 10)
    set_color(ctx, accent)
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(6.5)
    ctx.stroke()

    draw_rounded_rect(ctx, -w / 2 + 12, -h - 38, w - 24, 38, 8)
    set_color(ctx, PALETTE_CREAM["white"])
    ctx.fill_preserve()
    set_color(ctx, ink)
    ctx.set_line_width(5.0)
    ctx.stroke()

    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(21.0)
    set_color(ctx, ink)
    ext = ctx.text_extents(label)
    ctx.move_to(-ext.width / 2, -h - 12)
    ctx.show_text(label)

    cols, rows = 3, 4
    win_w, win_h = (w - 48) / cols, (h - 90) / rows
    for r in range(rows):
        for c in range(cols):
            wx = -w / 2 + 16 + c * (win_w + 8)
            wy = -h + 22 + r * (win_h + 10)
            draw_rounded_rect(ctx, wx, wy, win_w - 4, win_h - 4, 4)
            set_color(ctx, PALETTE_CREAM["white"])
            ctx.fill_preserve()
            set_color(ctx, ink)
            ctx.set_line_width(3.5)
            ctx.stroke()

    draw_rounded_rect(ctx, -22, -42, 44, 42, 6)
    set_color(ctx, ink)
    ctx.fill()
    ctx.restore()

def draw_money_bundle(ctx, x, y, scale=1.0, angle=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.scale(scale, scale)

    ctx.move_to(-48, -12)
    ctx.line_to(12, -26)
    ctx.line_to(48, -4)
    ctx.line_to(48, 15)
    ctx.line_to(-12, 29)
    ctx.line_to(-48, 7)
    ctx.close_path()
    set_color(ctx, PALETTE_CREAM["green"], alpha)
    ctx.fill_preserve()
    set_color(ctx, PALETTE_CREAM["ink"], alpha)
    ctx.set_line_width(4.0)
    ctx.stroke()

    ctx.move_to(-22, -18)
    ctx.line_to(14, 4)
    ctx.line_to(14, 23)
    ctx.line_to(-6, 28)
    ctx.line_to(-6, 9)
    ctx.line_to(-38, -13)
    ctx.close_path()
    set_color(ctx, PALETTE_CREAM["white"], alpha)
    ctx.fill_preserve()
    set_color(ctx, PALETTE_CREAM["ink"], alpha)
    ctx.set_line_width(3.0)
    ctx.stroke()
    ctx.restore()

def draw_coin(ctx, x, y, r=20.0, scale=1.0):
    if scale <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    set_color(ctx, PALETTE_CREAM["gold"])
    ctx.fill_preserve()
    set_color(ctx, PALETTE_CREAM["ink"])
    ctx.set_line_width(4.5)
    ctx.stroke()
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(r * 1.15)
    ext = ctx.text_extents("$")
    ctx.move_to(-ext.width / 2, ext.height * 0.36)
    ctx.show_text("$")
    ctx.restore()

# ==============================================================================
# 3. PROCEDURAL SOUND EFFECTS & AUDIO MIXING ENGINE
# ==============================================================================

def generate_sfx_track(output_wav_path, duration_sec, events, *, fundo=True):
    sr = 44100
    n_samples = int(duration_sec * sr)
    buf = [0.0] * n_samples
    rng = random.Random(303)

    if fundo:
        for i in range(n_samples):
            t = i / sr
            beat = (t * 1.85) % 1.0
            env = math.exp(-beat * 6.0)
            tone = math.sin(2 * math.pi * 110.0 * t) * 0.5 + math.sin(2 * math.pi * 165.0 * t) * 0.3
            buf[i] += tone * env * 0.018

    for ev_time, ev_type, vol in events:
        idx0 = int(ev_time * sr)
        if ev_type == "pop":
            dur = int(0.09 * sr)
            for j in range(dur):
                if idx0 + j >= n_samples:
                    break
                u = j / dur
                freq = lerp(280.0, 720.0, u)
                env = math.sin(u * math.pi) * math.exp(-u * 2.5)
                buf[idx0 + j] += math.sin(2 * math.pi * freq * (j / sr)) * env * vol
        elif ev_type == "whoosh":
            dur = int(0.28 * sr)
            lp = 0.0
            for j in range(dur):
                if idx0 + j >= n_samples:
                    break
                u = j / dur
                env = math.sin(u * math.pi) ** 1.5
                noise = rng.uniform(-1.0, 1.0)
                alpha_f = 0.05 + 0.22 * math.sin(u * math.pi)
                lp = lp + alpha_f * (noise - lp)
                buf[idx0 + j] += lp * env * vol * 1.8
        elif ev_type == "cash":
            dur = int(0.45 * sr)
            for j in range(dur):
                if idx0 + j >= n_samples:
                    break
                u = j / dur
                t_loc = j / sr
                env = math.exp(-u * 5.0)
                bell = (
                    math.sin(2 * math.pi * 2093.0 * t_loc) * 0.5
                    + math.sin(2 * math.pi * 2637.0 * t_loc) * 0.4
                    + math.sin(2 * math.pi * 3136.0 * t_loc) * 0.3
                )
                buf[idx0 + j] += bell * env * vol
        elif ev_type == "paper_flip":
            dur = int(0.32 * sr)
            lp = 0.0
            for j in range(dur):
                if idx0 + j >= n_samples:
                    break
                u = j / dur
                env = math.sin(u * math.pi) * math.exp(-u * 2.0)
                noise = rng.uniform(-1.0, 1.0)
                lp = 0.7 * lp + 0.3 * noise
                buf[idx0 + j] += lp * env * vol

    with wave.open(output_wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        packed = bytearray()
        for s in buf:
            val = int(clamp(s, -0.98, 0.98) * 32767)
            packed.extend(struct.pack("<h", val))
        wf.writeframes(packed)

# ==============================================================================
# 4. MASTER 1-MINUTE 60 FPS RENDERER (WITH MOUTHLESS PUPPETS + RICH SCENERY)
# ==============================================================================

def render_video(timeline_path, output_mp4_path, external_audio_path=None):
    with open(timeline_path, "r") as f:
        timeline = json.load(f)

    total_duration = timeline[-1]["end"] + 0.75
    fps = 60
    width, height = 1920, 1080
    total_frames = int(total_duration * fps)

    print(f"[Palito YouTube Engine] Pre-rendering Dual-World textures ({width}x{height})...")
    bg_cream_surf = create_paper_background(width, height, world="cream")
    bg_kraft_surf = create_paper_background(width, height, world="kraft")

    segs = {item["id"]: item for item in timeline}
    t_s1 = segs.get("seg01", timeline[0])["start"]
    t_s2 = segs.get("seg02", timeline[min(1, len(timeline)-1)])["start"]
    t_s3 = segs.get("seg03", timeline[min(2, len(timeline)-1)])["start"]
    t_s4 = segs.get("seg04", timeline[min(3, len(timeline)-1)])["start"]
    t_s5 = segs.get("seg05", timeline[min(4, len(timeline)-1)])["start"]
    t_s6 = segs.get("seg06", timeline[min(5, len(timeline)-1)])["start"]
    t_s7 = segs.get("seg07", timeline[min(6, len(timeline)-1)])["start"]

    # ------------------------------------------------------------------
    # Dynamic 2D Camera Choreography ("Jogo de Câmeras")
    # ------------------------------------------------------------------
    cam = Camera2D()
    # Scene 1: Hook MCU on Mouthless Narrator (#1 Cap+Headphones) -> Pull-back to Glass Office Lobby with King (#14) & Wizard (#5)
    cam.add_shot(0.0, 0.1, 960, 565, 1.85, 960, 565, 1.85)
    cam.add_shot(1.4, 2.2, 960, 565, 1.85, 960, 520, 1.0, ease_in_out_cubic)
    # Scene 2: Pan left to Wizard (#5) & Smartphone Feed, then Whip-Pan right to Pirate (#13) & Diver (#21)
    cam.add_shot(t_s2, t_s2 + 0.75, 960, 520, 1.0, 580, 540, 1.25, ease_in_out_cubic)
    cam.add_shot(t_s2 + 3.2, t_s2 + 4.0, 580, 540, 1.25, 1340, 540, 1.25, ease_in_out_cubic)
    cam.add_shot(t_s2 + 6.2, t_s2 + 6.9, 1340, 540, 1.25, 960, 540, 1.0, ease_in_out_cubic)
    # Scene 3: Zoom into Scientist (#6), Engineer (#7), 3D Book & 4-Piece Interlocking Puzzle Grid
    cam.add_shot(t_s3, t_s3 + 0.8, 960, 540, 1.0, 960, 540, 1.12, ease_in_out_cubic)
    # Scene 4: Step 1 Security Reserve - Knight (#30) + Firefighter (#15) + Police (#17) + Vault Shield (Tesouro Selic / CDB 100% CDI)
    cam.add_shot(t_s4, t_s4 + 0.8, 960, 540, 1.12, 960, 540, 1.0, ease_in_out_cubic)
    # Scene 5: Step 2 Passive Income - Farmer (#16), Detective (#3) & Samurai (#19) with FIIs & Stock Towers + Foreground Narrator!
    cam.add_shot(t_s5, t_s5 + 0.8, 960, 540, 1.0, 860, 535, 1.04, ease_in_out_cubic)
    # Scene 6: 3D Kraft Board Drop -> Authentic Gas Station & Detailed Sage-Green Sedan Comparison + Foreground Narrator!
    cam.add_shot(t_s6, t_s6 + 0.85, 860, 535, 1.04, 880, 540, 1.0, ease_in_out_cubic)
    # Scene 7: Zoom into Superhero (#8), Astronaut (#10), Viking (#26) & Aviator (#24) riding the Compound Snowball -> Full Cast Finale!
    cam.add_shot(t_s7, t_s7 + 0.9, 880, 540, 1.0, 1180, 530, 1.18, ease_in_out_cubic)
    cam.add_shot(t_s7 + 4.5, t_s7 + 5.3, 1180, 530, 1.18, 960, 540, 1.0, ease_in_out_cubic)

    sfx_events = [
        (1.4, "whoosh", 0.38),
        (2.1, "pop", 0.38),
        (3.1, "pop", 0.38),
        (t_s2, "whoosh", 0.38),
        (t_s2 + 1.2, "pop", 0.35),
        (t_s2 + 3.2, "whoosh", 0.38),
        (t_s2 + 6.2, "whoosh", 0.35),
        (t_s3, "pop", 0.40),
        (t_s3 + 1.8, "pop", 0.38),
        (t_s3 + 3.0, "pop", 0.38),
        (t_s4, "whoosh", 0.38),
        (t_s4 + 1.5, "pop", 0.42),
        (t_s4 + 3.5, "cash", 0.42),
        (t_s5, "whoosh", 0.38),
        (t_s5 + 1.4, "pop", 0.38),
        (t_s5 + 2.4, "pop", 0.38),
        (t_s5 + 4.5, "cash", 0.45),
        (t_s5 + 6.5, "cash", 0.45),
        (t_s6 - 0.35, "paper_flip", 0.52),
        (t_s6 + 1.0, "pop", 0.38),
        (t_s7, "whoosh", 0.40),
        (t_s7 + 2.0, "cash", 0.48),
        (t_s7 + 4.5, "paper_flip", 0.45),
        (t_s7 + 5.2, "cash", 0.50),
    ]

    scratch_dir = os.path.dirname(os.path.abspath(timeline_path))
    sfx_wav = os.path.join(scratch_dir, "sfx_v3.wav")
    master_aac = os.path.join(scratch_dir, "master_v3.m4a")
    generate_sfx_track(sfx_wav, total_duration, sfx_events)

    unique_files = list({item.get("file") for item in timeline if item.get("file")})
    single_audio = external_audio_path or (unique_files[0] if len(unique_files) == 1 else None)

    if single_audio and os.path.exists(single_audio):
        print(f"[Palito YouTube Engine] Mixing single external audio track ({single_audio}) with procedural SFX...")
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "warning",
                "-i", sfx_wav,
                "-i", single_audio,
                "-filter_complex", "[1:a]volume=1.18[vo];[0:a][vo]amix=inputs=2:normalize=0,alimiter=limit=0.95[outa]",
                "-map", "[outa]",
                "-c:a", "aac", "-b:a", "192k",
                "-t", f"{total_duration:.3f}",
                master_aac,
            ],
            check=True,
        )
    else:
        print("[Palito YouTube Engine] Mixing TTS segments with procedural SFX...")
        ff_inputs = ["-i", sfx_wav]
        delay_filters = []
        mix_labels = ["[0:a]"]
        for idx, item in enumerate(timeline):
            ff_inputs.extend(["-i", item["file"]])
            ms = int(item["start"] * 1000)
            lbl = f"[a{idx+1}]"
            delay_filters.append(f"[{idx+1}:a]adelay={ms}|{ms},volume=1.18{lbl}")
            mix_labels.append(lbl)

        filter_str = ";".join(delay_filters) + f";{''.join(mix_labels)}amix=inputs={len(mix_labels)}:normalize=0,alimiter=limit=0.95[outa]"
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "warning",
                *ff_inputs,
                "-filter_complex", filter_str,
                "-map", "[outa]",
                "-c:a", "aac", "-b:a", "192k",
                "-t", f"{total_duration:.3f}",
                master_aac,
            ],
            check=True,
        )

    print(f"[Super-Skill v3] Rendering {total_frames} frames at 60 FPS (1920x1080)...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-loglevel", "warning",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "bgra",
        "-s", f"{width}x{height}",
        "-r", str(fps),
        "-i", "-",
        "-i", master_aac,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-shortest",
        output_mp4_path,
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    t_board_drop = t_s6 - 0.45

    for frame_idx in range(total_frames):
        t = frame_idx / fps

        # 1. Dual-World Textured Background
        ctx.save()
        ctx.identity_matrix()
        in_kraft_world = (t >= t_s6) and (t < t_s7 + 4.6)
        ctx.set_source_surface(bg_kraft_surf if in_kraft_world else bg_cream_surf, 0, 0)
        ctx.paint()
        ctx.restore()

        # 2. Apply Virtual 2D Camera Transform
        ctx.save()
        ctx.identity_matrix()
        cam.apply(ctx, t)

        # ==============================================================
        # SCENE 1 (0 -> t_s2): OFFICE LOBBY ENVIRONMENT + MOUTHLESS PUPPETS (#1, #14, #5)
        # ==============================================================
        if t < t_s2:
            # Glass Office Lobby with Potted Plants & Waiting Bench in background
            if t >= 1.2:
                draw_office_lobby_environment(ctx, t=t)

            # Mouthless Narrator (#1 Cap+Headphones)
            draw_puppet_30(
                ctx, 960, 845,
                scale=1.35, t=t,
                archetype="1_cap_gamer",
                world="cream",
                pose="present_both" if t > 1.8 else "idle",
                expression="neutral",
            )
            if t >= 1.85:
                s_k = ease_out_back(prog(t, 1.85, 2.35))
                draw_puppet_30(ctx, 510, 845, scale=1.28 * s_k, t=t, archetype="14_king", pose="hips", expression="neutral")
                draw_curved_banner_text(ctx, "MUITO DINHEIRO?", 510, 480, 175, progress=prog(t, 2.0, 2.7), font_size=26)

            if t >= 2.95:
                s_w = ease_out_back(prog(t, 2.95, 3.45))
                draw_puppet_30(ctx, 1410, 845, scale=1.28 * s_w, t=t, archetype="5_wizard", pose="point_left", expression="neutral")
                draw_curved_banner_text(ctx, "FÓRMULA MÁGICA?", 1410, 480, 175, progress=prog(t, 3.1, 3.8), font_size=26)

        # ==============================================================
        # SCENE 2 (t_s2 -> t_s3): SMARTPHONE FEED + WIZARD (#5), CLOWN (#20), PIRATE (#13) & DIVER (#21)
        # ==============================================================
        elif t < t_s3:
            # Giant Smartphone scrolling feed in center
            s_ph = ease_out_back(prog(t, t_s2 + 0.3, t_s2 + 0.85))
            draw_smartphone_feed(ctx, 960, 560, scale=0.85 * s_ph, world="cream", scroll_offset=t * 95.0)

            # Left: Wizard (#5) & Clown (#20) trying to guess the market with a magnifier
            s_w = ease_out_back(prog(t, t_s2, t_s2 + 0.5))
            draw_puppet_30(
                ctx, 430, 855, scale=1.28 * s_w, t=t,
                archetype="5_wizard",
                pose="point_right",
                expression="sad" if t > t_s2 + 5.8 else "determined",
                prop_r="magnifier",
            )
            draw_puppet_30(
                ctx, 660, 855, scale=1.18 * s_w, t=t,
                archetype="20_clown",
                pose="shrug" if t > t_s2 + 5.8 else "cheer",
                expression="sad" if t > t_s2 + 5.8 else "neutral",
            )
            draw_curved_banner_text(ctx, "ADIVINHAR O MERCADO", 545, 455, 195, progress=prog(t, t_s2 + 0.4, t_s2 + 1.4), font_size=24)

            # Right: Pirate (#13) & Diver (#21) chasing quick treasure
            if t >= t_s2 + 2.8:
                s_p = ease_out_back(prog(t, t_s2 + 2.8, t_s2 + 3.35))
                p_expr = "sad" if t > t_s2 + 5.8 else "determined"
                draw_puppet_30(ctx, 1270, 855, scale=1.28 * s_p, t=t, archetype="13_pirate", pose="shrug" if t > t_s2 + 5.8 else "cheer", expression=p_expr)
                draw_puppet_30(ctx, 1510, 855, scale=1.22 * s_p, t=t, archetype="21_diver", pose="idle", expression=p_expr)
                draw_curved_banner_text(ctx, "LUCRO RÁPIDO?", 1390, 455, 185, progress=prog(t, t_s2 + 3.3, t_s2 + 4.2), font_size=25)

        # ==============================================================
        # SCENE 3 (t_s3 -> t_s4): 3D BOOK + INTERLOCKING PUZZLE + SCIENTIST (#6), ENGINEER (#7), ARTIST (#9)
        # ==============================================================
        elif t < t_s4:
            s_in = ease_out_back(prog(t, t_s3, t_s3 + 0.5))
            # 3D Hardcover Investing Book on left
            draw_3d_book(ctx, 320, 520, "O INVESTIDOR", "INTELIGENTE", "OS 3 PILARES", scale=0.78 * s_in, angle=-0.06)

            # Scientist (#6) & Engineer (#7) & Artist (#9) assembling the 4-Piece Puzzle Grid!
            draw_puppet_30(ctx, 610, 860, scale=1.26 * s_in, t=t, archetype="6_scientist", pose="point_right", expression="happy_eyes")
            draw_puppet_30(ctx, 1340, 860, scale=1.26 * s_in, t=t, archetype="7_engineer", pose="hips", expression="neutral")
            draw_puppet_30(ctx, 1580, 860, scale=1.22 * s_in, t=t, archetype="9_artist", pose="point_left", expression="neutral")

            sep = 1.0 - ease_out_cubic(prog(t, t_s3 + 1.2, t_s3 + 3.2))
            draw_puzzle_grid_2x2(ctx, 975, 430, separation=sep, scale=0.95 * s_in)

        # ==============================================================
        # SCENE 4 (t_s4 -> t_s5): PASSO 1: RESERVA DE SEGURANÇA (#30 Knight, #15 Firefighter, #17 Police)
        # ==============================================================
        elif t < t_s5:
            s_kn = ease_out_back(prog(t, t_s4, t_s4 + 0.5))
            draw_puppet_30(ctx, 360, 860, scale=1.32 * s_kn, t=t, archetype="30_knight", pose="point_right", expression="determined")
            draw_puppet_30(ctx, 610, 860, scale=1.26 * s_kn, t=t, archetype="15_firefighter", pose="hips", expression="neutral")
            draw_puppet_30(ctx, 1320, 860, scale=1.26 * s_kn, t=t, archetype="17_police", pose="hips", expression="determined")
            draw_puppet_30(ctx, 1560, 860, scale=1.28 * s_kn, t=t, archetype="1_cap_gamer", pose="present_both", expression="happy_eyes")

            s_sh = ease_out_back(prog(t, t_s4 + 0.4, t_s4 + 1.0))
            draw_vault_shield(ctx, 960, 620, scale=1.12 * s_sh, t=t)

            if t >= t_s4 + 2.0:
                s_b1 = ease_out_back(prog(t, t_s4 + 2.0, t_s4 + 2.5))
                draw_badge_card(ctx, 710, 265, 420, 125, "PASSO 1: LIQUIDEZ DIÁRIA", "TESOURO SELIC", scale=s_b1, accent=PALETTE_CREAM["ink"])
            if t >= t_s4 + 4.0:
                s_b2 = ease_out_back(prog(t, t_s4 + 4.0, t_s4 + 4.5))
                draw_badge_card(ctx, 1210, 265, 420, 125, "SEGURANÇA TOTAL", "CDB 100% CDI", scale=s_b2, accent=PALETTE_CREAM["green"])

        # ==============================================================
        # SCENE 5 (t_s5 -> t_s6): PASSO 2: FIIs & AÇÕES (#16 Farmer, #3 Detective, #19 Samurai, #12 Cowboy)
        # ==============================================================
        elif t < t_s6:
            s_f = ease_out_back(prog(t, t_s5, t_s5 + 0.5))
            draw_puppet_30(ctx, 260, 870, scale=1.25 * s_f, t=t, archetype="16_farmer", pose="present_both", expression="happy_eyes")
            draw_puppet_30(ctx, 480, 870, scale=1.25 * s_f, t=t, archetype="19_samurai", pose="hips", expression="determined")
            draw_puppet_30(ctx, 1420, 870, scale=1.25 * s_f, t=t, archetype="3_detective", pose="point_left", expression="neutral")

            if t >= t_s5 + 1.0:
                sb1 = ease_out_back(prog(t, t_s5 + 1.0, t_s5 + 1.55))
                draw_fii_building(ctx, 760, 870, 235, 340, "FIIs (IMÓVEIS)", scale=sb1, accent=PALETTE_CREAM["mid"])
            if t >= t_s5 + 2.0:
                sb2 = ease_out_back(prog(t, t_s5 + 2.0, t_s5 + 2.55))
                draw_fii_building(ctx, 1130, 870, 235, 390, "AÇÕES (EMPRESAS)", scale=sb2, accent=PALETTE_CREAM["ink"])

            if t >= t_s5 + 3.5:
                for k in range(6):
                    cy_coin = 260 + ((t * 165.0 + k * 75.0) % 340.0)
                    cx_coin = 700 + k * 90 + math.sin(t * 5.0 + k) * 14.0
                    draw_coin(ctx, cx_coin, cy_coin, r=22.0)

                s_div = ease_out_back(prog(t, t_s5 + 3.7, t_s5 + 4.2))
                draw_badge_card(ctx, 945, 200, 520, 115, "PASSO 2: RENDA PASSIVA MENSAL", "ALUGUÉIS + DIVIDENDOS ($)", scale=s_div, accent=PALETTE_CREAM["green"])

        # ==============================================================
        # SCENE 6 & 7 (t_s6 -> End): KRAFT STORYBOARD WORLD (GAS STATION SCREENSHOT REPLICA + COMPOUND SNOWBALL!)
        # ==============================================================
        else:
            if t < t_s7:
                # REPLICA OF USER'S UPLOADED SCREENSHOT IN KRAFT WORLD!
                # Detailed Gas Station with 7-segment LCD prices (5.20, 4.50, 3.80, 4.80) + oil-drop canopy + dual-nozzle pump
                s_st = ease_out_back(prog(t, t_s6 + 0.15, t_s6 + 0.75))
                draw_detailed_gas_station(ctx, 890, 595, scale=0.92 * s_st, brand="red", is_closed=False, t=t)

                # Two Mouthless High-Vis Attendants on the Left holding Tire Pressure Gauge & Long Window Squeegee!
                draw_puppet_30(
                    ctx, 180, 775, scale=1.08 * s_st, t=t,
                    archetype="7_engineer", world="kraft",
                    pose="wave_right", expression="happy_eyes",
                    prop_l="tire_gauge", high_vis_vest=True,
                )
                draw_puppet_30(
                    ctx, 325, 740, scale=1.10 * s_st, t=t + 0.5,
                    archetype="7_engineer", world="kraft",
                    pose="wave_right", expression="happy_eyes",
                    prop_l="squeegee", high_vis_vest=True,
                )

                # Detailed Sage-Green Sedan Car with 6-spoke wheels & waving Mouthless Driver (#3 Detective) inside!
                car_slide = ease_out_cubic(prog(t, t_s6 + 0.4, t_s6 + 1.6))
                car_x = lerp(420.0, 825.0, car_slide)
                draw_detailed_sedan_car(
                    ctx, car_x, 755, scale=1.32, flip_x=False,
                    driver_archetype="3_detective", world="kraft", t=t,
                )

            elif t < t_s7 + 4.6:
                # Second half of Kraft World: Exponential Compound Interest Snowball Curve!
                ink_k = PALETTE_KRAFT["ink"]
                draw_badge_card(ctx, 500, 195, 420, 110, "SEM REINVESTIR", "DINHEIRO PARADO", scale=ease_out_back(prog(t, t_s7, t_s7 + 0.5)), accent=PALETTE_KRAFT["red"], ink=ink_k)
                draw_puppet_30(ctx, 380, 855, scale=1.22, t=t, archetype="22_vampire", world="kraft", pose="shrug", expression="sad")
                draw_puppet_30(ctx, 580, 855, scale=1.22, t=t, archetype="2_chef", world="kraft", pose="idle", expression="sad")

                draw_badge_card(ctx, 1340, 195, 460, 110, "PASSO 3: JUROS COMPOSTOS", "BOLA DE NEVE EXPONENCIAL!", scale=ease_out_back(prog(t, t_s7 + 0.3, t_s7 + 0.8)), accent=PALETTE_CREAM["green"], ink=ink_k)

                u_curve = prog(t, t_s7 + 0.4, t_s7 + 3.2)
                ctx.save()
                ctx.set_line_width(11.0)
                set_color(ctx, PALETTE_CREAM["green"])
                ctx.move_to(940, 840)
                n_pts = int(40 * clamp(u_curve, 0.05, 1.0))
                for idx_p in range(1, n_pts + 1):
                    up = (idx_p / 40.0) * clamp(u_curve, 0.05, 1.0)
                    px = lerp(940.0, 1620.0, up)
                    py = 840.0 - (up ** 2.8) * 520.0
                    ctx.line_to(px, py)
                ctx.stroke()
                ctx.restore()

                n_stacks = int(lerp(2, 18, prog(t, t_s7 + 0.5, t_s7 + 3.5)))
                for s_idx in range(n_stacks):
                    col = s_idx % 6
                    row = s_idx // 6
                    draw_money_bundle(ctx, 1060 + col * 85, 845 - row * 38, scale=0.88)

                draw_puppet_30(ctx, 1150, 735, scale=1.24, t=t, archetype="8_superhero", world="kraft", pose="cheer", expression="happy_eyes")
                draw_puppet_30(ctx, 1370, 725, scale=1.24, t=t, archetype="10_astronaut", world="kraft", pose="cheer")
                draw_puppet_30(ctx, 1580, 735, scale=1.22, t=t, archetype="26_viking", world="kraft", pose="cheer", expression="determined")

            else:
                # Grand Finale (t_s7 + 4.6 -> End): Back to Cream World with 8-Character Showcase Cast!
                s_fin = ease_out_back(prog(t, t_s7 + 4.6, t_s7 + 5.15))
                draw_badge_card(ctx, 960, 200, 760, 130, "LIBERDADE FINANCEIRA EM 3 PASSOS", "COMECE HOJE MESMO (A PARTIR DE R$ 50)!", scale=s_fin, accent=PALETTE_CREAM["green"])

                cast = [
                    (200, "30_knight", "hips"),
                    (415, "6_scientist", "present_both"),
                    (630, "11_ninja", "hips"),
                    (845, "1_cap_gamer", "cheer"),
                    (1065, "8_superhero", "hips"),
                    (1280, "14_king", "present_both"),
                    (1495, "18_rockstar", "cheer"),
                    (1710, "10_astronaut", "cheer"),
                ]
                for (cx_c, arch_c, po_c) in cast:
                    draw_puppet_30(ctx, cx_c, 865, scale=1.16 * s_fin, t=t, archetype=arch_c, world="cream", pose=po_c, expression="happy_eyes")

        ctx.restore()  # End Camera Transform

        # ==============================================================
        # 3. SCREEN-SPACE OVERLAYS (FOREGROUND NARRATOR & 3D KRAFT BOARD WIPE!)
        # ==============================================================
        # A. Foreground Narrator Overlay in bottom-right corner during Scene 5 & Scene 6 (exact match to screenshot!)
        if t_s5 + 3.0 <= t <= t_s7 - 0.2:
            enter_u = ease_out_cubic(prog(t, t_s5 + 3.0, t_s5 + 3.6)) * (1.0 - prog(t, t_s7 - 0.7, t_s7 - 0.2))
            fg_world = "kraft" if in_kraft_world else "cream"
            draw_foreground_narrator(
                ctx,
                t=t,
                side="right",
                archetype="classic_narrator",
                world=fg_world,
                enter_progress=enter_u,
                pose="idle",
            )

        # B. 3D Kraft Paper Board Wipe Transition entering Scene 6
        if t_board_drop <= t <= t_s6 + 0.05:
            u_drop = ease_in_out_cubic(prog(t, t_board_drop, t_s6))
            draw_kraft_board_wipe(ctx, u_drop)

        proc.stdin.write(surface.get_data())

        if frame_idx % 600 == 0 and frame_idx > 0:
            print(f"  -> Rendered {frame_idx}/{total_frames} frames ({frame_idx/total_frames*100:.0f}%)")

    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg exited with code {proc.returncode}")
    print(f"[Super-Skill v3] Successfully rendered 60 FPS video to: {output_mp4_path}")

if __name__ == "__main__":
    ext_audio = None
    if "--external-audio" in sys.argv:
        idx_a = sys.argv.index("--external-audio")
        ext_audio = sys.argv[idx_a + 1]
    render_video(sys.argv[1], sys.argv[2], external_audio_path=ext_audio)
