<!-- Canonical document conversion specification — SSOT for engine tiers, formats, and integration -->
<!-- REFERENCE, DO NOT PASTE -->

# Document Conversion Specification

## Purpose

Convert binary documents (PDF, DOCX, PPTX, XLSX, images) to markdown for wiki ingestion via `wiki-add --file`. Conversion is a transparent pre-processing step — the A→W→R pipeline always receives markdown.

## Tiered Engine Architecture

| Priority | Engine | License | Install | Strengths | Weakness |
|----------|--------|---------|---------|-----------|----------|
| 1 (default) | Kreuzberg | MIT | `pip install kreuzberg>=4.9` | Cross-platform, no GPU, 97+ formats, lightweight | Tables flatten |
| 2 (accuracy) | Docling | Apache 2.0 | `pip install docling` (Mac: `docling[mlx]`) | Best tables/layout, MLX accel | Heavy (~2GB models) |
| 3 (fallback) | Pandoc | GPL-2 | System install (`brew`/`apt`/`winget`) | Zero Python deps, DOCX reliable | DOCX only |

Engine selection: explicit `--engine` flag > auto-detect (try 1→2→3). Per-wiki `schema.md` `conversion.preferred_engine` is read by the skill layer (wiki-add SKILL.md) and passed as `--engine`.

## Supported Format Matrix

| Extension | Kreuzberg | Docling | Pandoc |
|-----------|-----------|---------|--------|
| .pdf | Yes | Yes (best tables) | No |
| .docx | Yes | Yes | Yes |
| .pptx | Yes | Yes | No |
| .xlsx | Yes | Yes | No |
| .html | Yes | Yes | Yes |
| .png/.jpg/.tiff | Yes (OCR) | Yes (OCR) | No |
| .epub | No | No | Yes |
| .md/.txt/.rst | Passthrough | Passthrough | Passthrough |

## CLI Interface

```
convert.py --file <path> [--engine kreuzberg|docling|pandoc]
convert.py --formats          # list supported formats
convert.py --engines          # show installed engines
```

Output: UTF-8 markdown to stdout. Exit codes: 0 success, 1 conversion error, 2 no engine available.

## Wiki-Add Integration

In `wiki-add/SKILL.md` Step 1, binary formats are detected by extension and converted before the analyst receives them. The analyst is unaware of which engine performed conversion. See `wiki-add/SKILL.md` for the pre-processing flow.

## Per-Wiki Engine Preference

Optional field in `schema.md`:

```yaml
conversion:
  preferred_engine: kreuzberg | docling | pandoc
```

Allows domain-specific defaults (e.g., AML wiki defaults to Docling for regulatory tables).

## Installation

### Minimum (all platforms)
```
pip install kreuzberg>=4.9
```

### Accuracy upgrade (Mac with Apple Silicon)
```
pip install "docling[mlx]"
```

### Accuracy upgrade (Windows/Linux)
```
pip install docling
```

### DOCX-only fallback
```
# Mac: brew install pandoc
# Windows: winget install pandoc
# Linux: apt install pandoc
```
