# Camera Choreography, Dual-World Modes & Scene Composition Guide

This guide documents the exact directing, camera movement, and environmental staging patterns extracted from the original 12-minute video (`Once You Learn To Copy You'll Never Lack Money Again`).

---

## 1. Dual-World Color & Mood Architecture

The original video alternates between two distinct visual worlds to keep the viewer's brain engaged during 10+ minute videos:

### World A: The Concept Canvas (`PALETTE_CREAM`)
- **Background**: `#F5EDD6` warm parchment paper with subtle radial vignette and organic grain speckles.
- **Line & Primary Fill**: `#0F4B58` (Deep Petrol Teal).
- **Secondary Fill**: `#53848E` (Muted Slate Teal).
- **Highlight / Glass Fill**: `#A3C3C8` (Soft Ice Teal).
- **Accent Pops**: `#63CB6C` (Money Green), `#EEC03C` (Gold), `#DC5348` (Alert Coral Red).

### World B: The Analogy / Case-Study Storyboard (`PALETTE_KRAFT`)
- **When to Trigger**: Whenever the script says *"Imagine..."*, *"Let me show you a story..."*, or enters a concrete real-world business comparison (e.g., two gas stations, two restaurants, two YouTube channels).
- **Entry Transition (`draw_kraft_board_wipe`)**:
  - A giant tilted kraft board (`#C7B59C`) is pulled diagonally from top-right to bottom-left by a teal-sleeved hand gripping the board's edge.
  - Accompanied by a `paper_flip` sound effect.
- **Palette Shift Inside World B**:
  - Background becomes `#C7B59C` (Earthy Sepia Kraft Paper).
  - All character outlines and fills shift from teal to **`#3D2B24` (Dark Espresso Brown)**.
  - Props use warm sepia-harmonized accents: `#A8584C` (Brick Terracotta Red), `#88A070` (Sage Olive Green — used on the detailed sedan car), `#E8C55A` (Mustard Yellow safety vests), and `#D8CFC2` (Concrete/Steel pillars).
- **Exit Transition**: The board slides back diagonally to reveal the Cream Canvas for the lesson's takeaway.

---

## 2. The "Foreground Narrator Overlay" (2.5D Depth Technique)

Look at frame `01:23` (your uploaded screenshot):
- While the full environment (gas station, price totem, car with driver, and two waving attendants holding a pressure gauge and squeegee) plays in the background at `scale = 0.85`, **the Narrator pops up in the bottom-right foreground at `scale = 1.65` (`x = 1660, y = 1260`)**.
- Because `y = 1260` is below the `1080p` frame bottom, the narrator is framed from the chest up (Medium Close-Up), looking toward the background scene (`look_dir = (-5, -2)`).
- **How to use**: Call `draw_foreground_narrator(ctx, t, side="right", archetype="1_cap_gamer", ink_color=...)` in screen-space *after* `ctx.restore()` of the camera transform, so the narrator stays anchored in the foreground corner even while the camera pans across the background scene!

---

## 3. Signature Camera Moves (`Camera2D`)

1. **The Hook Push/Pull (`00:00 – 00:02`)**:
   - Start at `zoom = 1.95` focused on the narrator's upper body (`cx = 960, cy = 470`).
   - At the first punchword, pull back with `ease_in_out_cubic` over `0.65s` to `zoom = 1.0` (`cx = 960, cy = 540`).
2. **The Horizontal Whip-Pan (`ease_in_out_cubic` over `0.55s – 0.75s`)**:
   - Place Competitor A at `x = 520` and Competitor B at `x = 1400`.
   - Establish both at `zoom = 1.0`, then pan + zoom into Competitor A (`cx = 550, cy = 560, zoom = 1.48`), hold for 3–4s while cars/money animate, then whip-pan right to Competitor B (`cx = 1370, cy = 560, zoom = 1.48`).
3. **The Magnifying Glass Inspection (`draw_magnifying_glass`)**:
   - When the narrator says *"observe what works"* or *"look closely at the details"*, animate a vector magnifying glass sweeping across the target prop (e.g., mobile screen, storefront, or financial chart).
4. **The Binocular Cutout Mask (`draw_binocular_mask`)**:
   - Dark overlay with two overlapping circular cutouts that pop in with `ease_out_back` when focusing on a mentor or target business.
5. **The Puzzle-Piece Assembly (`draw_puzzle_grid_2x2`)**:
   - Four interlocking puzzle pieces featuring icons or mentor portraits that slide together from the corners (`dx, dy -> 0`) to represent combining ideas from multiple sources.
