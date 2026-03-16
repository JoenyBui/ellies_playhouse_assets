#!/usr/bin/env python3
"""
Modular Animal Character SVG Generator
=======================================
Generates chibi-style modular animal character parts as SVG files.
All SVGs share a 512x512 coordinate space so parts layer correctly.

Based on Kenney's Modular Characters structure, adapted for animal characters.
"""

import os
import math

# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_DIR = os.path.join(BASE_DIR, "SVG")

# ---------------------------------------------------------------------------
# Animal color palettes (extracted from source character images)
# ---------------------------------------------------------------------------
ANIMALS = {
    "tiger": {
        "primary": "#F5B731",       # golden yellow
        "secondary": "#FCE4A8",     # cream belly
        "accent": "#3D2B1F",        # dark stripes
        "outline": "#2D1F10",
        "nose_color": "#3D2B1F",
    },
    "whale": {
        "primary": "#6BA3C7",       # blue
        "secondary": "#D4E8F1",     # light blue belly
        "accent": "#4A7A9B",        # dark blue
        "outline": "#2D4A5E",
        "nose_color": "#2D4A5E",
    },
    "panda": {
        "primary": "#FAFAFA",       # white
        "secondary": "#FFFFFF",     # white belly
        "accent": "#2D2D2D",        # black patches
        "outline": "#1A1A1A",
        "nose_color": "#2D2D2D",
    },
    "koala": {
        "primary": "#8B7BB5",       # purple-grey
        "secondary": "#D4C8E8",     # light purple belly
        "accent": "#6B5B95",        # dark purple
        "outline": "#3D3055",
        "nose_color": "#2D2D2D",
    },
    "chicken": {
        "primary": "#E8943A",       # orange
        "secondary": "#FCE4C0",     # cream belly
        "accent": "#D4722B",        # darker orange
        "outline": "#6B3A15",
        "nose_color": "#E8B83A",    # yellow beak
    },
    "cardinal": {
        "primary": "#CC2222",       # red
        "secondary": "#E86B3A",     # orange-red chest
        "accent": "#2D2D2D",        # black mask
        "outline": "#5C1111",
        "nose_color": "#E88A2A",    # orange beak
    },
    "elk": {
        "primary": "#9B7653",       # brown
        "secondary": "#F0DCC0",     # cream belly
        "accent": "#5C4033",        # dark brown
        "outline": "#3D2B1F",
        "nose_color": "#3D2B1F",
    },
    "wolf": {
        "primary": "#8E9EAB",       # grey
        "secondary": "#D4DDE3",     # light grey belly
        "accent": "#5C6B76",        # dark grey
        "outline": "#3A444D",
        "nose_color": "#2D2D2D",
    },
    "water_buffalo": {
        "primary": "#E8A0B0",       # pink
        "secondary": "#F5C8D5",     # light pink belly
        "accent": "#C47888",        # dark pink
        "outline": "#7A3A4A",
        "nose_color": "#7A3A4A",
    },
    "lizard": {
        "primary": "#7BC45A",       # green
        "secondary": "#C8E8B0",     # light green belly
        "accent": "#E8C83A",        # yellow spots
        "outline": "#2D5A1F",
        "nose_color": "#2D5A1F",
    },
}

# ---------------------------------------------------------------------------
# Layout constants (all SVGs use 512x512 coordinate space)
# ---------------------------------------------------------------------------
CANVAS = 512
HEAD_CX, HEAD_CY = 256, 175        # head center
HEAD_RX, HEAD_RY = 115, 110        # head radii
BODY_CX, BODY_CY = 256, 345        # body center
BODY_RX, BODY_RY = 85, 95          # body radii
EYE_Y = 170                        # eye vertical center
EYE_SPACING = 48                   # distance from center to each eye
EYE_R = 22                         # eye radius
MOUTH_Y = 220                      # mouth vertical center
NOSE_Y = 200                       # nose vertical center
STROKE_W = 5                       # standard outline width


# ---------------------------------------------------------------------------
# SVG helpers
# ---------------------------------------------------------------------------
def svg_header(width=CANVAS, height=CANVAS):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">\n'
    )

SVG_FOOTER = '</svg>\n'


def write_svg(path, content, width=CANVAS, height=CANVAS):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(svg_header(width, height))
        f.write(content)
        f.write(SVG_FOOTER)
    print(f"  wrote {os.path.relpath(path, BASE_DIR)}")


def ellipse(cx, cy, rx, ry, fill, stroke=None, stroke_width=STROKE_W, opacity=1.0, extra=""):
    sw = f' stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ''
    op = f' opacity="{opacity}"' if opacity < 1.0 else ''
    return f'  <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"{sw}{op}{extra}/>\n'


def circle(cx, cy, r, fill, stroke=None, stroke_width=STROKE_W, extra=""):
    sw = f' stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ''
    return f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{sw}{extra}/>\n'


def rect(x, y, w, h, fill, rx=0, stroke=None, stroke_width=STROKE_W):
    sw = f' stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ''
    corner = f' rx="{rx}" ry="{rx}"' if rx else ''
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{corner}{sw}/>\n'


def path(d, fill="none", stroke=None, stroke_width=STROKE_W, stroke_linecap="round", extra=""):
    parts = [f'  <path d="{d}" fill="{fill}"']
    if stroke:
        parts.append(f' stroke="{stroke}" stroke-width="{stroke_width}" stroke-linecap="{stroke_linecap}"')
    if extra:
        parts.append(f' {extra}')
    parts.append('/>\n')
    return ''.join(parts)


def polygon(points_list, fill, stroke=None, stroke_width=STROKE_W, stroke_linejoin="round"):
    pts = " ".join(f"{x},{y}" for x, y in points_list)
    sw = f' stroke="{stroke}" stroke-width="{stroke_width}" stroke-linejoin="{stroke_linejoin}"' if stroke else ''
    return f'  <polygon points="{pts}" fill="{fill}"{sw}/>\n'


# ---------------------------------------------------------------------------
# FACE: Eyes
# ---------------------------------------------------------------------------
def generate_eyes():
    print("\n=== Generating Eyes ===")
    d = os.path.join(SVG_DIR, "Face", "Eyes")

    # --- Happy eyes: large round with sparkle ---
    s = ""
    for sign in (-1, 1):
        ex = HEAD_CX + sign * EYE_SPACING
        # White of eye
        s += ellipse(ex, EYE_Y, EYE_R, EYE_R + 2, "#FFFFFF", "#1A1A1A", 4)
        # Iris
        s += circle(ex + sign * 3, EYE_Y + 2, EYE_R - 6, "#5C3A1A")
        # Pupil
        s += circle(ex + sign * 3, EYE_Y + 2, EYE_R - 12, "#1A1A1A")
        # Sparkle highlight
        s += circle(ex + sign * 6, EYE_Y - 5, 5, "#FFFFFF")
        s += circle(ex + sign * 1, EYE_Y + 4, 2.5, "#FFFFFF")
    write_svg(os.path.join(d, "eyes_happy.svg"), s)

    # --- Surprised eyes: extra wide ---
    s = ""
    for sign in (-1, 1):
        ex = HEAD_CX + sign * EYE_SPACING
        s += ellipse(ex, EYE_Y, EYE_R + 4, EYE_R + 6, "#FFFFFF", "#1A1A1A", 4)
        s += circle(ex, EYE_Y, EYE_R - 4, "#5C3A1A")
        s += circle(ex, EYE_Y, EYE_R - 10, "#1A1A1A")
        s += circle(ex + sign * 5, EYE_Y - 6, 6, "#FFFFFF")
        s += circle(ex + sign * 0, EYE_Y + 5, 3, "#FFFFFF")
    write_svg(os.path.join(d, "eyes_surprised.svg"), s)

    # --- Sad eyes: droopy ---
    s = ""
    for sign in (-1, 1):
        ex = HEAD_CX + sign * EYE_SPACING
        s += ellipse(ex, EYE_Y + 4, EYE_R - 2, EYE_R - 4, "#FFFFFF", "#1A1A1A", 4)
        s += circle(ex, EYE_Y + 6, EYE_R - 10, "#5C3A1A")
        s += circle(ex, EYE_Y + 6, EYE_R - 15, "#1A1A1A")
        s += circle(ex + sign * 3, EYE_Y + 1, 4, "#FFFFFF")
        # Sad eyebrow built into the eye shape - droopy upper lid
        bx1 = ex - sign * 18
        bx2 = ex + sign * 18
        s += path(
            f"M {bx1} {EYE_Y - 8} Q {ex} {EYE_Y - 18 + sign * 6} {bx2} {EYE_Y - 4}",
            stroke="#1A1A1A", stroke_width=4
        )
    write_svg(os.path.join(d, "eyes_sad.svg"), s)

    # --- Angry eyes: narrow, angled ---
    s = ""
    for sign in (-1, 1):
        ex = HEAD_CX + sign * EYE_SPACING
        s += ellipse(ex, EYE_Y, EYE_R, EYE_R - 6, "#FFFFFF", "#1A1A1A", 4)
        s += ellipse(ex + sign * 2, EYE_Y + 2, EYE_R - 8, EYE_R - 10, "#5C3A1A")
        s += ellipse(ex + sign * 2, EYE_Y + 2, EYE_R - 13, EYE_R - 13, "#1A1A1A")
        s += circle(ex + sign * 5, EYE_Y - 3, 3.5, "#FFFFFF")
        # Angry brow line
        bx1 = ex - sign * 20
        bx2 = ex + sign * 22
        s += path(
            f"M {bx1} {EYE_Y - 16 - sign * 4} L {bx2} {EYE_Y - 10 + sign * 4}",
            stroke="#1A1A1A", stroke_width=5
        )
    write_svg(os.path.join(d, "eyes_angry.svg"), s)

    # --- Sleepy eyes: half-closed ---
    s = ""
    for sign in (-1, 1):
        ex = HEAD_CX + sign * EYE_SPACING
        # Half-circle (bottom half of eye visible)
        s += f'  <clipPath id="sleepy_clip_{1 if sign > 0 else 0}"><rect x="{ex - EYE_R - 5}" y="{EYE_Y - 2}" width="{(EYE_R + 5) * 2}" height="{EYE_R + 10}"/></clipPath>\n'
        clip_id = f"sleepy_clip_{1 if sign > 0 else 0}"
        s += ellipse(ex, EYE_Y, EYE_R - 2, EYE_R - 2, "#FFFFFF", "#1A1A1A", 4,
                     extra=f' clip-path="url(#{clip_id})"')
        s += circle(ex, EYE_Y + 4, EYE_R - 10, "#5C3A1A",
                    extra=f' clip-path="url(#{clip_id})"')
        # Heavy eyelid line
        s += path(
            f"M {ex - EYE_R - 2} {EYE_Y} Q {ex} {EYE_Y - 6} {ex + EYE_R + 2} {EYE_Y}",
            stroke="#1A1A1A", stroke_width=5
        )
    write_svg(os.path.join(d, "eyes_sleepy.svg"), s)

    # --- Wink eyes: one open, one closed ---
    s = ""
    # Left eye: open
    ex = HEAD_CX - EYE_SPACING
    s += ellipse(ex, EYE_Y, EYE_R, EYE_R + 2, "#FFFFFF", "#1A1A1A", 4)
    s += circle(ex + 3, EYE_Y + 2, EYE_R - 6, "#5C3A1A")
    s += circle(ex + 3, EYE_Y + 2, EYE_R - 12, "#1A1A1A")
    s += circle(ex + 6, EYE_Y - 5, 5, "#FFFFFF")
    # Right eye: wink (curved line)
    ex = HEAD_CX + EYE_SPACING
    s += path(
        f"M {ex - 16} {EYE_Y + 2} Q {ex} {EYE_Y - 12} {ex + 16} {EYE_Y + 2}",
        stroke="#1A1A1A", stroke_width=5
    )
    write_svg(os.path.join(d, "eyes_wink.svg"), s)


# ---------------------------------------------------------------------------
# FACE: Mouths
# ---------------------------------------------------------------------------
def generate_mouths():
    print("\n=== Generating Mouths ===")
    d = os.path.join(SVG_DIR, "Face", "Mouth")

    # --- Smile: cute closed-mouth curve ---
    s = path(
        f"M {HEAD_CX - 22} {MOUTH_Y} Q {HEAD_CX} {MOUTH_Y + 18} {HEAD_CX + 22} {MOUTH_Y}",
        stroke="#1A1A1A", stroke_width=4
    )
    write_svg(os.path.join(d, "mouth_smile.svg"), s)

    # --- Open smile: D-shaped open mouth ---
    s = path(
        f"M {HEAD_CX - 24} {MOUTH_Y} Q {HEAD_CX} {MOUTH_Y + 28} {HEAD_CX + 24} {MOUTH_Y}",
        fill="#1A1A1A", stroke="#1A1A1A", stroke_width=3
    )
    # Tongue hint
    s += ellipse(HEAD_CX, MOUTH_Y + 14, 10, 7, "#E86B6B")
    # Teeth top edge
    s += path(
        f"M {HEAD_CX - 20} {MOUTH_Y + 2} L {HEAD_CX + 20} {MOUTH_Y + 2}",
        stroke="#FFFFFF", stroke_width=3
    )
    write_svg(os.path.join(d, "mouth_open_smile.svg"), s)

    # --- Oh: round surprised mouth ---
    s = ellipse(HEAD_CX, MOUTH_Y + 6, 12, 16, "#1A1A1A", "#1A1A1A", 3)
    s += ellipse(HEAD_CX, MOUTH_Y + 4, 6, 8, "#5C2020")
    write_svg(os.path.join(d, "mouth_oh.svg"), s)

    # --- Sad: downturned frown ---
    s = path(
        f"M {HEAD_CX - 20} {MOUTH_Y + 6} Q {HEAD_CX} {MOUTH_Y - 10} {HEAD_CX + 20} {MOUTH_Y + 6}",
        stroke="#1A1A1A", stroke_width=4
    )
    write_svg(os.path.join(d, "mouth_sad.svg"), s)

    # --- Tongue: playful tongue sticking out ---
    s = path(
        f"M {HEAD_CX - 22} {MOUTH_Y} Q {HEAD_CX} {MOUTH_Y + 14} {HEAD_CX + 22} {MOUTH_Y}",
        fill="#1A1A1A", stroke="#1A1A1A", stroke_width=3
    )
    # Tongue
    s += ellipse(HEAD_CX, MOUTH_Y + 16, 10, 14, "#E86B6B", "#C44A4A", 2)
    # Tongue line
    s += path(
        f"M {HEAD_CX} {MOUTH_Y + 8} L {HEAD_CX} {MOUTH_Y + 26}",
        stroke="#C44A4A", stroke_width=1.5
    )
    write_svg(os.path.join(d, "mouth_tongue.svg"), s)

    # --- Teeth: big toothy grin ---
    s = path(
        f"M {HEAD_CX - 26} {MOUTH_Y - 2} Q {HEAD_CX} {MOUTH_Y + 26} {HEAD_CX + 26} {MOUTH_Y - 2}",
        fill="#1A1A1A", stroke="#1A1A1A", stroke_width=3
    )
    # White teeth
    for i in range(-2, 3):
        tx = HEAD_CX + i * 10
        s += rect(tx - 4, MOUTH_Y - 1, 8, 10, "#FFFFFF", rx=2)
    write_svg(os.path.join(d, "mouth_teeth.svg"), s)


# ---------------------------------------------------------------------------
# FACE: Eyebrows (standalone, for animals that don't have brows built into eyes)
# ---------------------------------------------------------------------------
def generate_eyebrows():
    print("\n=== Generating Eyebrows ===")
    d = os.path.join(SVG_DIR, "Face", "Eyebrows")
    brow_y = EYE_Y - 30

    # --- Neutral ---
    s = ""
    for sign in (-1, 1):
        bx = HEAD_CX + sign * EYE_SPACING
        s += path(
            f"M {bx - 16} {brow_y} Q {bx} {brow_y - 6} {bx + 16} {brow_y}",
            stroke="#3D2B1F", stroke_width=5
        )
    write_svg(os.path.join(d, "brow_neutral.svg"), s)

    # --- Raised ---
    s = ""
    for sign in (-1, 1):
        bx = HEAD_CX + sign * EYE_SPACING
        s += path(
            f"M {bx - 16} {brow_y + 2} Q {bx} {brow_y - 14} {bx + 16} {brow_y + 2}",
            stroke="#3D2B1F", stroke_width=5
        )
    write_svg(os.path.join(d, "brow_raised.svg"), s)

    # --- Angry ---
    s = ""
    for sign in (-1, 1):
        bx = HEAD_CX + sign * EYE_SPACING
        s += path(
            f"M {bx - sign * 18} {brow_y - 6} L {bx + sign * 18} {brow_y + 6}",
            stroke="#3D2B1F", stroke_width=6
        )
    write_svg(os.path.join(d, "brow_angry.svg"), s)

    # --- Sad / worried ---
    s = ""
    for sign in (-1, 1):
        bx = HEAD_CX + sign * EYE_SPACING
        s += path(
            f"M {bx - sign * 18} {brow_y + 4} Q {bx} {brow_y - 10} {bx + sign * 18} {brow_y - 4}",
            stroke="#3D2B1F", stroke_width=5
        )
    write_svg(os.path.join(d, "brow_sad.svg"), s)


# ---------------------------------------------------------------------------
# FACE: Noses
# ---------------------------------------------------------------------------
def generate_noses():
    print("\n=== Generating Noses ===")
    d = os.path.join(SVG_DIR, "Face", "Nose")

    # --- Round button nose ---
    s = ellipse(HEAD_CX, NOSE_Y, 10, 8, "#2D2D2D", "#1A1A1A", 2)
    s += circle(HEAD_CX - 3, NOSE_Y - 2, 2.5, "#555555")  # highlight
    write_svg(os.path.join(d, "nose_round.svg"), s)

    # --- Triangle cat/fox nose ---
    s = polygon(
        [(HEAD_CX, NOSE_Y + 8), (HEAD_CX - 10, NOSE_Y - 5), (HEAD_CX + 10, NOSE_Y - 5)],
        fill="#2D2D2D", stroke="#1A1A1A", stroke_width=2
    )
    s += circle(HEAD_CX - 2, NOSE_Y - 2, 2, "#555555")
    write_svg(os.path.join(d, "nose_triangle.svg"), s)

    # --- Short bird beak (chicken) ---
    s = polygon(
        [(HEAD_CX, NOSE_Y + 12), (HEAD_CX - 14, NOSE_Y - 6), (HEAD_CX + 14, NOSE_Y - 6)],
        fill="#E8B83A", stroke="#B8882A", stroke_width=3
    )
    write_svg(os.path.join(d, "nose_beak_short.svg"), s)

    # --- Pointed bird beak (cardinal) ---
    s = polygon(
        [(HEAD_CX, NOSE_Y + 18), (HEAD_CX - 12, NOSE_Y - 4), (HEAD_CX + 12, NOSE_Y - 4)],
        fill="#E88A2A", stroke="#B86A1A", stroke_width=3
    )
    write_svg(os.path.join(d, "nose_beak_pointed.svg"), s)

    # --- Snout (for elk, water buffalo) ---
    s = ellipse(HEAD_CX, NOSE_Y + 4, 18, 12, "#D4A87A", "#8B6B4A", 3)
    # Nostrils
    s += ellipse(HEAD_CX - 6, NOSE_Y + 5, 3.5, 4, "#6B4A30")
    s += ellipse(HEAD_CX + 6, NOSE_Y + 5, 3.5, 4, "#6B4A30")
    write_svg(os.path.join(d, "nose_snout.svg"), s)


# ---------------------------------------------------------------------------
# HEADS: Per-animal head shapes
# ---------------------------------------------------------------------------
def generate_heads():
    print("\n=== Generating Heads ===")
    d = os.path.join(SVG_DIR, "Head")

    for name, colors in ANIMALS.items():
        s = ""
        pri = colors["primary"]
        sec = colors["secondary"]
        out = colors["outline"]

        if name == "whale":
            # Whale: rounder, slightly wider head
            s += ellipse(HEAD_CX, HEAD_CY, HEAD_RX + 15, HEAD_RY + 5, pri, out, STROKE_W)
            # Lighter face patch
            s += ellipse(HEAD_CX, HEAD_CY + 15, HEAD_RX - 20, HEAD_RY - 30, sec)
        elif name == "chicken":
            # Chicken: round with slight fluff on top
            s += ellipse(HEAD_CX, HEAD_CY, HEAD_RX - 5, HEAD_RY, pri, out, STROKE_W)
            s += ellipse(HEAD_CX, HEAD_CY + 15, HEAD_RX - 35, HEAD_RY - 30, sec)
        elif name == "cardinal":
            # Cardinal: round with pointed crest
            s += ellipse(HEAD_CX, HEAD_CY + 5, HEAD_RX - 5, HEAD_RY - 5, pri, out, STROKE_W)
            # Black mask area around eyes
            s += ellipse(HEAD_CX, EYE_Y, 55, 28, colors["accent"])
        elif name == "panda":
            # Panda: round white head
            s += ellipse(HEAD_CX, HEAD_CY, HEAD_RX, HEAD_RY, pri, out, STROKE_W)
            # Black eye patches
            s += ellipse(HEAD_CX - EYE_SPACING, EYE_Y, 30, 26, colors["accent"],
                         extra=' transform="rotate(-15, {}, {})"'.format(HEAD_CX - EYE_SPACING, EYE_Y))
            s += ellipse(HEAD_CX + EYE_SPACING, EYE_Y, 30, 26, colors["accent"],
                         extra=' transform="rotate(15, {}, {})"'.format(HEAD_CX + EYE_SPACING, EYE_Y))
        elif name == "water_buffalo":
            # Slightly wider head
            s += ellipse(HEAD_CX, HEAD_CY + 5, HEAD_RX + 5, HEAD_RY, pri, out, STROKE_W)
            s += ellipse(HEAD_CX, HEAD_CY + 20, HEAD_RX - 30, HEAD_RY - 40, sec)
        else:
            # Default round chibi head (tiger, koala, wolf, elk, lizard)
            s += ellipse(HEAD_CX, HEAD_CY, HEAD_RX, HEAD_RY, pri, out, STROKE_W)
            # Lighter face/cheek area
            s += ellipse(HEAD_CX, HEAD_CY + 10, HEAD_RX - 30, HEAD_RY - 30, sec)

        write_svg(os.path.join(d, f"head_{name}.svg"), s)


# ---------------------------------------------------------------------------
# BODIES: Per-animal body shapes
# ---------------------------------------------------------------------------
def generate_bodies():
    print("\n=== Generating Bodies ===")
    d = os.path.join(SVG_DIR, "Body")

    for name, colors in ANIMALS.items():
        s = ""
        pri = colors["primary"]
        sec = colors["secondary"]
        out = colors["outline"]

        if name == "whale":
            # Whale: tear-drop body, no legs
            s += ellipse(BODY_CX, BODY_CY - 10, BODY_RX + 10, BODY_RY + 15, pri, out, STROKE_W)
            # Belly
            s += ellipse(BODY_CX, BODY_CY, BODY_RX - 20, BODY_RY - 10, sec)
            # Tail fluke (at bottom)
            s += path(
                f"M {BODY_CX} {BODY_CY + 95} "
                f"Q {BODY_CX - 40} {BODY_CY + 120} {BODY_CX - 55} {BODY_CY + 105} "
                f"Q {BODY_CX - 30} {BODY_CY + 90} {BODY_CX} {BODY_CY + 95} Z",
                fill=pri, stroke=out, stroke_width=3
            )
            s += path(
                f"M {BODY_CX} {BODY_CY + 95} "
                f"Q {BODY_CX + 40} {BODY_CY + 120} {BODY_CX + 55} {BODY_CY + 105} "
                f"Q {BODY_CX + 30} {BODY_CY + 90} {BODY_CX} {BODY_CY + 95} Z",
                fill=pri, stroke=out, stroke_width=3
            )
        elif name in ("chicken", "cardinal"):
            # Birds: rounder, plumper body
            s += ellipse(BODY_CX, BODY_CY, BODY_RX - 5, BODY_RY + 5, pri, out, STROKE_W)
            s += ellipse(BODY_CX, BODY_CY + 5, BODY_RX - 30, BODY_RY - 25, sec)
        else:
            # Standard chibi body
            s += ellipse(BODY_CX, BODY_CY, BODY_RX, BODY_RY, pri, out, STROKE_W)
            # Belly patch
            s += ellipse(BODY_CX, BODY_CY + 5, BODY_RX - 25, BODY_RY - 20, sec)

        # Neck connector (small rect between head and body)
        neck_y = HEAD_CY + HEAD_RY - 10
        s += rect(HEAD_CX - 20, neck_y, 40, 30, pri)

        write_svg(os.path.join(d, f"body_{name}.svg"), s)


# ---------------------------------------------------------------------------
# EARS: Per-animal ear shapes
# ---------------------------------------------------------------------------
def generate_ears():
    print("\n=== Generating Ears ===")
    d = os.path.join(SVG_DIR, "Ears")

    for name, colors in ANIMALS.items():
        s = ""
        pri = colors["primary"]
        sec = colors["secondary"]
        out = colors["outline"]

        ear_top = HEAD_CY - HEAD_RY  # top of head

        if name == "tiger":
            # Rounded triangular ears
            for sign in (-1, 1):
                ex = HEAD_CX + sign * 75
                pts = [(ex, ear_top - 35), (ex - sign * 28, ear_top + 20), (ex + sign * 28, ear_top + 20)]
                s += polygon(pts, pri, out, STROKE_W)
                # Inner ear
                inner_pts = [(ex, ear_top - 20), (ex - sign * 16, ear_top + 12), (ex + sign * 16, ear_top + 12)]
                s += polygon(inner_pts, sec)

        elif name == "koala":
            # Big round fluffy ears
            for sign in (-1, 1):
                ex = HEAD_CX + sign * 95
                ey = HEAD_CY - 40
                s += ellipse(ex, ey, 42, 45, pri, out, STROKE_W)
                s += ellipse(ex, ey, 26, 28, "#E0C8F0")  # pink inner

        elif name == "panda":
            # Round black ears
            for sign in (-1, 1):
                ex = HEAD_CX + sign * 82
                ey = ear_top - 8
                s += circle(ex, ey, 30, colors["accent"], out, STROKE_W)

        elif name == "wolf":
            # Pointed ears with tufts
            for sign in (-1, 1):
                ex = HEAD_CX + sign * 70
                pts = [(ex, ear_top - 45), (ex - sign * 25, ear_top + 15), (ex + sign * 25, ear_top + 15)]
                s += polygon(pts, pri, out, STROKE_W)
                inner_pts = [(ex, ear_top - 30), (ex - sign * 14, ear_top + 8), (ex + sign * 14, ear_top + 8)]
                s += polygon(inner_pts, sec)

        elif name == "elk":
            # Small round ears + antlers
            for sign in (-1, 1):
                ex = HEAD_CX + sign * 75
                s += ellipse(ex, ear_top + 5, 16, 20, pri, out, 3)
                s += ellipse(ex, ear_top + 5, 9, 12, sec)
            # Antlers
            antler_color = "#8B6B42"
            antler_dark = "#5C4033"
            for sign in (-1, 1):
                ax = HEAD_CX + sign * 55
                ay = ear_top - 15
                # Main antler shaft
                s += path(
                    f"M {ax} {ay + 20} Q {ax + sign * 15} {ay - 10} {ax + sign * 25} {ay - 40}",
                    stroke=antler_color, stroke_width=8
                )
                # Branch 1
                s += path(
                    f"M {ax + sign * 15} {ay - 5} Q {ax + sign * 35} {ay - 15} {ax + sign * 40} {ay - 30}",
                    stroke=antler_color, stroke_width=6
                )
                # Branch 2
                s += path(
                    f"M {ax + sign * 22} {ay - 30} Q {ax + sign * 40} {ay - 35} {ax + sign * 45} {ay - 50}",
                    stroke=antler_color, stroke_width=5
                )
                # Tips
                for (tx, ty) in [(ax + sign * 25, ay - 40), (ax + sign * 40, ay - 30), (ax + sign * 45, ay - 50)]:
                    s += circle(tx, ty, 4, antler_color, antler_dark, 2)

        elif name == "water_buffalo":
            # Small ears + curved horns
            for sign in (-1, 1):
                ex = HEAD_CX + sign * 85
                s += ellipse(ex, ear_top + 15, 18, 14, pri, out, 3)
                s += ellipse(ex, ear_top + 15, 10, 8, sec)
            # Horns
            for sign in (-1, 1):
                hx = HEAD_CX + sign * 65
                hy = ear_top - 5
                s += path(
                    f"M {hx} {hy + 15} Q {hx + sign * 45} {hy - 20} {hx + sign * 30} {hy - 35}",
                    fill="none", stroke="#E8DCC0", stroke_width=14
                )
                s += path(
                    f"M {hx + sign * 30} {hy - 35} L {hx + sign * 28} {hy - 42}",
                    fill="none", stroke="#C8B898", stroke_width=10
                )

        elif name == "chicken":
            # Small comb on top
            cx_comb = HEAD_CX
            cy_comb = ear_top - 10
            for i in range(-1, 2):
                s += circle(cx_comb + i * 12, cy_comb - abs(i) * 5, 12, "#E83A3A", "#B82A2A", 2)
            # Wattle
            s += ellipse(HEAD_CX, MOUTH_Y + 25, 6, 10, "#E83A3A", "#B82A2A", 2)

        elif name == "cardinal":
            # Pointed crest
            cx_crest = HEAD_CX
            cy_crest = ear_top - 25
            pts = [(cx_crest, cy_crest - 20), (cx_crest - 15, ear_top + 5), (cx_crest + 15, ear_top + 5)]
            s += polygon(pts, pri, out, STROKE_W)

        elif name == "whale":
            # Dorsal fin on top
            cx_fin = HEAD_CX
            cy_fin = ear_top - 5
            pts = [(cx_fin, cy_fin - 30), (cx_fin - 20, cy_fin + 15), (cx_fin + 8, cy_fin + 15)]
            s += polygon(pts, colors["accent"], out, 3)

        elif name == "lizard":
            # Small ridges/bumps on top
            for i in range(-2, 3):
                lx = HEAD_CX + i * 20
                ly = ear_top - 5 + abs(i) * 3
                s += circle(lx, ly, 8 - abs(i), colors["accent"], out, 2)

        write_svg(os.path.join(d, f"ears_{name}.svg"), s)


# ---------------------------------------------------------------------------
# ARMS: Shared arm types
# ---------------------------------------------------------------------------
def generate_arms():
    print("\n=== Generating Arms ===")
    d = os.path.join(SVG_DIR, "Arms")

    for name, colors in ANIMALS.items():
        s = ""
        pri = colors["primary"]
        out = colors["outline"]

        arm_y = BODY_CY - 30  # shoulder height

        if name in ("chicken", "cardinal"):
            # Wings
            for sign in (-1, 1):
                ax = BODY_CX + sign * (BODY_RX + 10)
                # Wing shape (3 feathered bumps)
                s += path(
                    f"M {BODY_CX + sign * BODY_RX} {arm_y} "
                    f"Q {ax + sign * 15} {arm_y - 15} {ax + sign * 30} {arm_y} "
                    f"Q {ax + sign * 35} {arm_y + 15} {ax + sign * 25} {arm_y + 25} "
                    f"Q {ax + sign * 15} {arm_y + 30} {ax} {arm_y + 25} "
                    f"Q {BODY_CX + sign * (BODY_RX - 5)} {arm_y + 20} {BODY_CX + sign * BODY_RX} {arm_y} Z",
                    fill=pri, stroke=out, stroke_width=3
                )
        elif name == "whale":
            # Flippers
            for sign in (-1, 1):
                ax = BODY_CX + sign * (BODY_RX + 5)
                s += path(
                    f"M {BODY_CX + sign * BODY_RX} {arm_y + 10} "
                    f"Q {ax + sign * 30} {arm_y - 10} {ax + sign * 40} {arm_y + 15} "
                    f"Q {ax + sign * 30} {arm_y + 35} {BODY_CX + sign * BODY_RX} {arm_y + 30} Z",
                    fill=pri, stroke=out, stroke_width=3
                )
        else:
            # Standard paw arms
            for sign in (-1, 1):
                ax = BODY_CX + sign * (BODY_RX + 5)
                # Arm
                s += ellipse(ax + sign * 15, arm_y + 15, 22, 35, pri, out, STROKE_W,
                             extra=f' transform="rotate({sign * 15}, {ax + sign * 15}, {arm_y + 15})"')
                # Paw/hand circle
                s += circle(ax + sign * 25, arm_y + 45, 16, pri, out, 3)

        write_svg(os.path.join(d, f"arms_{name}.svg"), s)


# ---------------------------------------------------------------------------
# LEGS: Per-animal leg shapes
# ---------------------------------------------------------------------------
def generate_legs():
    print("\n=== Generating Legs ===")
    d = os.path.join(SVG_DIR, "Legs")

    for name, colors in ANIMALS.items():
        s = ""
        pri = colors["primary"]
        acc = colors.get("accent", pri)
        out = colors["outline"]

        leg_top = BODY_CY + BODY_RY - 30
        leg_bottom = BODY_CY + BODY_RY + 35

        if name == "whale":
            # No legs for whale - skip (tail fluke is part of body)
            write_svg(os.path.join(d, f"legs_{name}.svg"), "")
            continue

        if name in ("chicken", "cardinal"):
            # Bird legs: thin with claws
            for sign in (-1, 1):
                lx = BODY_CX + sign * 25
                # Thin leg
                s += rect(lx - 4, leg_top, 8, 50, "#E8943A" if name == "chicken" else "#E86B3A",
                          rx=4, stroke=out, stroke_width=2)
                # Claw foot
                for ci in (-1, 0, 1):
                    s += path(
                        f"M {lx} {leg_bottom + 5} L {lx + ci * 12} {leg_bottom + 18}",
                        stroke="#E8943A" if name == "chicken" else "#E86B3A", stroke_width=4
                    )
        else:
            # Standard stubby legs
            for sign in (-1, 1):
                lx = BODY_CX + sign * 30
                s += ellipse(lx, leg_top + 25, 22, 32, pri, out, STROKE_W)
                # Foot pad / sole
                s += ellipse(lx, leg_bottom + 5, 24, 12, acc, out, 3)

        write_svg(os.path.join(d, f"legs_{name}.svg"), s)


# ---------------------------------------------------------------------------
# TAILS: Per-animal tail shapes
# ---------------------------------------------------------------------------
def generate_tails():
    print("\n=== Generating Tails ===")
    d = os.path.join(SVG_DIR, "Tail")

    for name, colors in ANIMALS.items():
        s = ""
        pri = colors["primary"]
        acc = colors.get("accent", pri)
        out = colors["outline"]

        # Tail typically extends from behind the body
        tx = BODY_CX + BODY_RX - 10
        ty = BODY_CY + 20

        if name == "tiger":
            # Long curved tail with stripes
            s += path(
                f"M {tx} {ty} Q {tx + 60} {ty - 40} {tx + 70} {ty + 10} Q {tx + 80} {ty + 50} {tx + 55} {ty + 60}",
                fill="none", stroke=pri, stroke_width=16, stroke_linecap="round"
            )
            s += path(
                f"M {tx} {ty} Q {tx + 60} {ty - 40} {tx + 70} {ty + 10} Q {tx + 80} {ty + 50} {tx + 55} {ty + 60}",
                fill="none", stroke=out, stroke_width=20, stroke_linecap="round",
                extra='opacity="0.15"'
            )
            # Tip
            s += circle(tx + 55, ty + 60, 10, acc, out, 2)

        elif name == "wolf":
            # Bushy tail
            s += path(
                f"M {tx} {ty} Q {tx + 50} {ty - 30} {tx + 55} {ty + 20} "
                f"Q {tx + 60} {ty + 50} {tx + 35} {ty + 55} "
                f"Q {tx + 10} {ty + 50} {tx - 5} {ty + 30} Z",
                fill=pri, stroke=out, stroke_width=3
            )
            s += path(
                f"M {tx + 35} {ty + 55} Q {tx + 45} {ty + 40} {tx + 40} {ty + 25}",
                fill="none", stroke=colors["secondary"], stroke_width=8, stroke_linecap="round"
            )

        elif name == "lizard":
            # Long curved thin tail
            s += path(
                f"M {tx} {ty} Q {tx + 50} {ty + 10} {tx + 70} {ty + 40} "
                f"Q {tx + 85} {ty + 65} {tx + 75} {ty + 80}",
                fill="none", stroke=pri, stroke_width=12, stroke_linecap="round"
            )
            # Spots on tail
            for i, (sx, sy) in enumerate([(tx + 30, ty + 15), (tx + 55, ty + 40), (tx + 72, ty + 65)]):
                s += circle(sx, sy, 4 - i * 0.5, acc)

        elif name == "elk":
            # Short stubby tail
            s += ellipse(tx + 10, ty - 5, 12, 10, pri, out, 3)

        elif name == "panda":
            # Small round tail
            s += circle(tx + 8, ty - 5, 14, colors["accent"], out, 3)

        elif name in ("chicken", "cardinal"):
            # Tail feathers
            tail_cx = BODY_CX - BODY_RX + 5
            tail_cy = BODY_CY + 10
            for i in range(3):
                angle = -30 + i * 15
                s += ellipse(
                    tail_cx - 20, tail_cy - 10 + i * 8, 25, 10,
                    pri if i != 1 else acc, out, 2,
                    extra=f' transform="rotate({angle}, {tail_cx - 20}, {tail_cy - 10 + i * 8})"'
                )

        elif name == "water_buffalo":
            # Short thin tail with tuft
            s += path(
                f"M {tx} {ty} Q {tx + 30} {ty + 20} {tx + 25} {ty + 50}",
                fill="none", stroke=pri, stroke_width=6, stroke_linecap="round"
            )
            s += circle(tx + 25, ty + 52, 8, acc, out, 2)

        elif name == "whale":
            # Tail is part of body, but add a small reference
            s += ""  # handled in body

        elif name == "koala":
            # Koalas have barely visible tails - tiny bump
            s += ellipse(tx + 5, ty, 8, 6, pri, out, 2)

        write_svg(os.path.join(d, f"tail_{name}.svg"), s)


# ---------------------------------------------------------------------------
# MARKINGS: Per-animal pattern overlays
# ---------------------------------------------------------------------------
def generate_markings():
    print("\n=== Generating Markings ===")
    d = os.path.join(SVG_DIR, "Markings")

    for name, colors in ANIMALS.items():
        s = ""
        acc = colors.get("accent", colors["primary"])

        if name == "tiger":
            # Stripes on head
            for i, (sx, sy, angle, length) in enumerate([
                (HEAD_CX - 30, HEAD_CY - 60, -20, 20),
                (HEAD_CX, HEAD_CY - 70, 0, 22),
                (HEAD_CX + 30, HEAD_CY - 60, 20, 20),
                (HEAD_CX - 50, HEAD_CY + 5, -30, 16),
                (HEAD_CX + 50, HEAD_CY + 5, 30, 16),
            ]):
                rad = math.radians(angle)
                ex = sx + math.sin(rad) * length
                ey = sy - math.cos(rad) * length
                s += path(f"M {sx} {sy} L {ex} {ey}", stroke=acc, stroke_width=5, stroke_linecap="round")

            # Stripes on body
            for i, by in enumerate([BODY_CY - 30, BODY_CY, BODY_CY + 30]):
                for sign in (-1, 1):
                    bx = BODY_CX + sign * 40
                    s += path(
                        f"M {bx} {by - 8} L {bx + sign * 15} {by + 8}",
                        stroke=acc, stroke_width=4, stroke_linecap="round"
                    )

        elif name == "lizard":
            # Yellow spots
            spots = [
                (HEAD_CX - 40, HEAD_CY - 30, 5),
                (HEAD_CX + 35, HEAD_CY - 40, 4),
                (HEAD_CX - 20, HEAD_CY - 55, 3.5),
                (HEAD_CX + 50, HEAD_CY - 20, 4),
                (BODY_CX - 40, BODY_CY - 20, 5),
                (BODY_CX + 45, BODY_CY - 10, 4.5),
                (BODY_CX - 30, BODY_CY + 25, 4),
                (BODY_CX + 35, BODY_CY + 30, 3.5),
            ]
            for (sx, sy, sr) in spots:
                s += circle(sx, sy, sr, acc)

        elif name == "koala":
            # Subtle fur texture - lighter patches
            s += ellipse(HEAD_CX - 45, HEAD_CY + 5, 20, 15, colors["secondary"], opacity=0.4)
            s += ellipse(HEAD_CX + 45, HEAD_CY + 5, 20, 15, colors["secondary"], opacity=0.4)

        # Other animals can have empty markings (their base colors are sufficient)
        write_svg(os.path.join(d, f"markings_{name}.svg"), s)


# ---------------------------------------------------------------------------
# ACCESSORIES: Shared dress-up items
# ---------------------------------------------------------------------------
def generate_accessories():
    print("\n=== Generating Accessories ===")

    # --- HATS ---
    hat_dir = os.path.join(SVG_DIR, "Accessories", "Hats")
    hat_y = HEAD_CY - HEAD_RY - 5

    # Crown
    s = polygon(
        [(HEAD_CX - 50, hat_y + 15), (HEAD_CX - 50, hat_y - 20),
         (HEAD_CX - 30, hat_y - 5), (HEAD_CX - 15, hat_y - 35),
         (HEAD_CX, hat_y - 15), (HEAD_CX + 15, hat_y - 35),
         (HEAD_CX + 30, hat_y - 5), (HEAD_CX + 50, hat_y - 20),
         (HEAD_CX + 50, hat_y + 15)],
        fill="#FFD700", stroke="#DAA520", stroke_width=3
    )
    # Jewels
    s += circle(HEAD_CX - 25, hat_y - 8, 4, "#E83A3A")
    s += circle(HEAD_CX, hat_y - 20, 4, "#3A8AE8")
    s += circle(HEAD_CX + 25, hat_y - 8, 4, "#3AE83A")
    # Band
    s += rect(HEAD_CX - 52, hat_y + 10, 104, 10, "#DAA520", rx=3)
    write_svg(os.path.join(hat_dir, "hat_crown.svg"), s)

    # Party hat
    s = polygon(
        [(HEAD_CX, hat_y - 60), (HEAD_CX - 40, hat_y + 15), (HEAD_CX + 40, hat_y + 15)],
        fill="#E83A8A", stroke="#B82A6A", stroke_width=3
    )
    # Stripes
    for i in range(3):
        sy = hat_y + 15 - (i + 1) * 18
        hw = 40 - (i + 1) * 10
        s += path(
            f"M {HEAD_CX - hw} {sy} L {HEAD_CX + hw} {sy}",
            stroke="#FFD700", stroke_width=3
        )
    # Pom pom
    s += circle(HEAD_CX, hat_y - 60, 8, "#FFD700", "#DAA520", 2)
    write_svg(os.path.join(hat_dir, "hat_party.svg"), s)

    # Cowboy hat
    s = ellipse(HEAD_CX, hat_y + 10, 75, 12, "#8B6B42", "#5C4033", 3)  # brim
    s += path(  # crown
        f"M {HEAD_CX - 40} {hat_y + 5} "
        f"Q {HEAD_CX - 45} {hat_y - 30} {HEAD_CX - 20} {hat_y - 35} "
        f"Q {HEAD_CX} {hat_y - 28} {HEAD_CX + 20} {hat_y - 35} "
        f"Q {HEAD_CX + 45} {hat_y - 30} {HEAD_CX + 40} {hat_y + 5} Z",
        fill="#A0825A", stroke="#5C4033", stroke_width=3
    )
    s += rect(HEAD_CX - 38, hat_y - 2, 76, 8, "#5C4033", rx=2)  # band
    write_svg(os.path.join(hat_dir, "hat_cowboy.svg"), s)

    # Beanie
    s += ellipse(HEAD_CX, hat_y + 5, HEAD_RX + 5, 25, "#3A6AE8", "#2A4AB8", 3)
    s_beanie = ellipse(HEAD_CX, hat_y + 5, HEAD_RX + 5, 25, "#3A6AE8", "#2A4AB8", 3)
    s_beanie += path(
        f"M {HEAD_CX - HEAD_RX - 5} {hat_y + 5} "
        f"Q {HEAD_CX} {hat_y - 50} {HEAD_CX + HEAD_RX + 5} {hat_y + 5}",
        fill="#3A6AE8", stroke="#2A4AB8", stroke_width=3
    )
    # Ribbing lines
    for i in range(5):
        rx_offset = HEAD_CX - 50 + i * 25
        s_beanie += path(
            f"M {rx_offset} {hat_y + 15} L {rx_offset + 10} {hat_y - 10}",
            stroke="#2A5AD8", stroke_width=2
        )
    s_beanie += circle(HEAD_CX, hat_y - 45, 10, "#FFFFFF", "#DDD", 2)  # pom pom
    write_svg(os.path.join(hat_dir, "hat_beanie.svg"), s_beanie)

    # Top hat
    s = ellipse(HEAD_CX, hat_y + 8, 65, 12, "#2D2D2D", "#1A1A1A", 3)  # brim
    s += rect(HEAD_CX - 38, hat_y - 55, 76, 63, "#2D2D2D", rx=5, stroke="#1A1A1A", stroke_width=3)
    s += ellipse(HEAD_CX, hat_y - 55, 38, 8, "#3D3D3D", "#1A1A1A", 2)  # top
    s += rect(HEAD_CX - 38, hat_y - 10, 76, 10, "#8B2252", rx=0)  # ribbon
    write_svg(os.path.join(hat_dir, "hat_tophat.svg"), s)

    # --- GLASSES ---
    glasses_dir = os.path.join(SVG_DIR, "Accessories", "Glasses")

    # Round glasses
    s = ""
    for sign in (-1, 1):
        gx = HEAD_CX + sign * EYE_SPACING
        s += circle(gx, EYE_Y, EYE_R + 8, "none", "#3D2B1F", 3)
    # Bridge
    s += path(
        f"M {HEAD_CX - EYE_SPACING + EYE_R + 8} {EYE_Y} "
        f"Q {HEAD_CX} {EYE_Y - 8} "
        f"{HEAD_CX + EYE_SPACING - EYE_R - 8} {EYE_Y}",
        stroke="#3D2B1F", stroke_width=3
    )
    # Temple arms
    s += path(f"M {HEAD_CX - EYE_SPACING - EYE_R - 8} {EYE_Y} L {HEAD_CX - EYE_SPACING - EYE_R - 30} {EYE_Y + 5}",
              stroke="#3D2B1F", stroke_width=3)
    s += path(f"M {HEAD_CX + EYE_SPACING + EYE_R + 8} {EYE_Y} L {HEAD_CX + EYE_SPACING + EYE_R + 30} {EYE_Y + 5}",
              stroke="#3D2B1F", stroke_width=3)
    write_svg(os.path.join(glasses_dir, "glasses_round.svg"), s)

    # Sunglasses
    s = ""
    for sign in (-1, 1):
        gx = HEAD_CX + sign * EYE_SPACING
        s += rect(gx - EYE_R - 6, EYE_Y - EYE_R - 4, (EYE_R + 6) * 2, (EYE_R + 4) * 2,
                  "#1A1A1A", rx=8, stroke="#3D3D3D", stroke_width=3)
    s += path(
        f"M {HEAD_CX - EYE_SPACING + EYE_R + 6} {EYE_Y} L {HEAD_CX + EYE_SPACING - EYE_R - 6} {EYE_Y}",
        stroke="#3D3D3D", stroke_width=4
    )
    write_svg(os.path.join(glasses_dir, "glasses_sunglasses.svg"), s)

    # --- NECKWEAR ---
    neck_dir = os.path.join(SVG_DIR, "Accessories", "Neckwear")
    neck_y = HEAD_CY + HEAD_RY + 10

    # Bowtie
    s = polygon(
        [(HEAD_CX, neck_y), (HEAD_CX - 30, neck_y - 15), (HEAD_CX - 30, neck_y + 15)],
        fill="#E83A3A", stroke="#B82A2A", stroke_width=2
    )
    s += polygon(
        [(HEAD_CX, neck_y), (HEAD_CX + 30, neck_y - 15), (HEAD_CX + 30, neck_y + 15)],
        fill="#E83A3A", stroke="#B82A2A", stroke_width=2
    )
    s += circle(HEAD_CX, neck_y, 6, "#B82A2A")
    write_svg(os.path.join(neck_dir, "neck_bowtie.svg"), s)

    # Scarf
    s = path(
        f"M {HEAD_CX - 60} {neck_y - 5} "
        f"Q {HEAD_CX} {neck_y + 15} {HEAD_CX + 60} {neck_y - 5}",
        fill="#3A8AE8", stroke="#2A6AB8", stroke_width=3
    )
    # Scarf tails
    s += path(
        f"M {HEAD_CX + 20} {neck_y + 5} Q {HEAD_CX + 25} {neck_y + 40} {HEAD_CX + 15} {neck_y + 60}",
        fill="none", stroke="#3A8AE8", stroke_width=14, stroke_linecap="round"
    )
    s += path(
        f"M {HEAD_CX + 15} {neck_y + 10} Q {HEAD_CX + 35} {neck_y + 45} {HEAD_CX + 30} {neck_y + 65}",
        fill="none", stroke="#2A7AD8", stroke_width=12, stroke_linecap="round"
    )
    write_svg(os.path.join(neck_dir, "neck_scarf.svg"), s)

    # Necklace
    s = path(
        f"M {HEAD_CX - 55} {neck_y} Q {HEAD_CX} {neck_y + 30} {HEAD_CX + 55} {neck_y}",
        fill="none", stroke="#DAA520", stroke_width=3
    )
    # Pendant
    s += circle(HEAD_CX, neck_y + 28, 8, "#FFD700", "#DAA520", 2)
    s += circle(HEAD_CX, neck_y + 28, 4, "#E83A3A")
    write_svg(os.path.join(neck_dir, "neck_necklace.svg"), s)

    # --- PROPS ---
    props_dir = os.path.join(SVG_DIR, "Accessories", "Props")

    # Balloon (held in right hand area)
    px = BODY_CX + BODY_RX + 45
    py = HEAD_CY - 80
    s = path(f"M {px} {py + 55} L {px - 5} {BODY_CY - 20}", stroke="#888", stroke_width=1.5)
    s += ellipse(px, py, 28, 35, "#E83A8A", "#B82A6A", 2)
    s += ellipse(px - 6, py - 10, 6, 10, "#FFFFFF", opacity=0.3)
    # Knot
    s += polygon([(px - 3, py + 34), (px + 3, py + 34), (px, py + 40)], fill="#B82A6A")
    write_svg(os.path.join(props_dir, "prop_balloon.svg"), s)

    # Flower
    px = BODY_CX + BODY_RX + 40
    py = BODY_CY - 10
    # Stem
    s = path(f"M {px} {py} L {px - 5} {py + 50}", stroke="#4CAF50", stroke_width=4)
    # Leaf
    s += path(f"M {px - 3} {py + 30} Q {px - 20} {py + 25} {px - 15} {py + 35}", fill="#4CAF50")
    # Petals
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        petx = px + math.cos(rad) * 14
        pety = py + math.sin(rad) * 14
        s += circle(petx, pety, 10, "#FF69B4", "#E8508A", 1.5)
    # Center
    s += circle(px, py, 7, "#FFD700", "#DAA520", 1.5)
    write_svg(os.path.join(props_dir, "prop_flower.svg"), s)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"Generating modular character SVGs to: {SVG_DIR}\n")

    generate_eyes()
    generate_mouths()
    generate_eyebrows()
    generate_noses()
    generate_heads()
    generate_bodies()
    generate_ears()
    generate_arms()
    generate_legs()
    generate_tails()
    generate_markings()
    generate_accessories()

    # Count generated files
    count = 0
    for root, dirs, files in os.walk(SVG_DIR):
        count += sum(1 for f in files if f.endswith('.svg'))

    print(f"\n{'='*50}")
    print(f"Done! Generated {count} SVG files.")
    print(f"Output directory: {SVG_DIR}")


if __name__ == "__main__":
    main()
