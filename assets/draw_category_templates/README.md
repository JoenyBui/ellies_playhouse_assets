# Draw Category Templates

This folder stores seeded tracing-template PNG assets for Draw Category.

## Generation Pipeline (Recommended: Deterministic Simple Shapes)

Generate clean toddler-friendly single-shape templates (no API key, no online model dependency):

```bash
python scripts/generate_simple_draw_templates.py \
  --prompts shared/DrawCategory/prompts.json \
  --out-dir assets/draw_category_templates \
  --stroke 14
```

Then validate coverage and image checks:

```bash
python scripts/validate_draw_category_templates.py
```

## Optional AI Batch Pipeline

If needed, AI generation inputs are still available via:
- `scripts/build_draw_category_template_jobs.py`
- `assets/draw_category_templates/draw_category_template_jobs.jsonl`

## Naming Contract

- Exactly one PNG per seeded Draw Category prompt ID.
- Filename format: `<prompt-id>.png`.
- Expected default dimensions: `1024x1024` with transparent background.
