#!/usr/bin/env python3
"""
Assembles modular SVG layers into combined character preview SVGs.
Creates one assembled character per animal for visual verification.
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_DIR = os.path.join(BASE_DIR, "SVG")
PREVIEW_DIR = os.path.join(BASE_DIR, "preview_assembled")

ANIMALS = [
    'tiger', 'panda', 'koala', 'wolf', 'elk',
    'chicken', 'cardinal', 'whale', 'water_buffalo', 'lizard'
]

DEFAULT_NOSE = {
    'tiger': 'nose_triangle', 'panda': 'nose_round', 'koala': 'nose_round',
    'wolf': 'nose_triangle', 'elk': 'nose_snout', 'chicken': 'nose_beak_short',
    'cardinal': 'nose_beak_pointed', 'whale': 'nose_round',
    'water_buffalo': 'nose_snout', 'lizard': 'nose_round'
}


def extract_svg_content(filepath):
    """Extract the inner content of an SVG file (everything between <svg> tags)."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        # Remove the <svg ...> opening and </svg> closing tags
        content = re.sub(r'<svg[^>]*>', '', content)
        content = content.replace('</svg>', '')
        return content.strip()
    except FileNotFoundError:
        return ''


def assemble_character(animal, eyes='eyes_happy', mouth='mouth_smile',
                       hat=None, glasses=None, neck=None):
    """Assemble a full character from modular SVG parts."""
    nose = DEFAULT_NOSE.get(animal, 'nose_round')

    # Layer order (back to front)
    layers = [
        os.path.join(SVG_DIR, "Tail", f"tail_{animal}.svg"),
        os.path.join(SVG_DIR, "Body", f"body_{animal}.svg"),
        os.path.join(SVG_DIR, "Legs", f"legs_{animal}.svg"),
        os.path.join(SVG_DIR, "Arms", f"arms_{animal}.svg"),
        os.path.join(SVG_DIR, "Head", f"head_{animal}.svg"),
        os.path.join(SVG_DIR, "Ears", f"ears_{animal}.svg"),
        os.path.join(SVG_DIR, "Markings", f"markings_{animal}.svg"),
        os.path.join(SVG_DIR, "Face", "Eyes", f"{eyes}.svg"),
        os.path.join(SVG_DIR, "Face", "Nose", f"{nose}.svg"),
        os.path.join(SVG_DIR, "Face", "Mouth", f"{mouth}.svg"),
    ]

    if hat:
        layers.append(os.path.join(SVG_DIR, "Accessories", "Hats", f"{hat}.svg"))
    if glasses:
        layers.append(os.path.join(SVG_DIR, "Accessories", "Glasses", f"{glasses}.svg"))
    if neck:
        layers.append(os.path.join(SVG_DIR, "Accessories", "Neckwear", f"{neck}.svg"))

    # Combine all layers
    combined = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">\n'
    combined += '  <!-- Background -->\n'
    combined += '  <rect width="512" height="512" fill="#E8F0F8" rx="20"/>\n'

    for layer_path in layers:
        content = extract_svg_content(layer_path)
        if content:
            layer_name = os.path.basename(layer_path).replace('.svg', '')
            combined += f'  <!-- {layer_name} -->\n'
            combined += f'  <g id="{layer_name}">\n'
            combined += f'    {content}\n'
            combined += f'  </g>\n'

    combined += '</svg>\n'
    return combined


def main():
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    print(f"Assembling character previews to: {PREVIEW_DIR}\n")

    # Generate a preview for each animal with default settings
    for animal in ANIMALS:
        svg_content = assemble_character(animal)
        output_path = os.path.join(PREVIEW_DIR, f"assembled_{animal}.svg")
        with open(output_path, 'w') as f:
            f.write(svg_content)
        print(f"  assembled_{animal}.svg")

    # Generate a fun hybrid: tiger with cowboy hat and sunglasses
    svg_content = assemble_character(
        'tiger', eyes='eyes_wink', mouth='mouth_teeth',
        hat='hat_cowboy', glasses='glasses_sunglasses'
    )
    output_path = os.path.join(PREVIEW_DIR, "assembled_tiger_cowboy.svg")
    with open(output_path, 'w') as f:
        f.write(svg_content)
    print("  assembled_tiger_cowboy.svg (bonus: cowboy tiger!)")

    # Panda with crown and bowtie
    svg_content = assemble_character(
        'panda', eyes='eyes_happy', mouth='mouth_open_smile',
        hat='hat_crown', neck='neck_bowtie'
    )
    output_path = os.path.join(PREVIEW_DIR, "assembled_panda_fancy.svg")
    with open(output_path, 'w') as f:
        f.write(svg_content)
    print("  assembled_panda_fancy.svg (bonus: fancy panda!)")

    print(f"\nDone! Open the SVGs in a browser or image viewer to inspect.")


if __name__ == "__main__":
    main()
