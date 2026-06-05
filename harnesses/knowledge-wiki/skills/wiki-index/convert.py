#!/usr/bin/env python3
"""Convert documents to markdown for wiki ingestion.

Tiered engine selection:
  1. Kreuzberg (default — cross-platform, lightweight, no GPU)
  2. Docling (accuracy upgrade — complex tables, layout analysis)
  3. Pandoc (DOCX-only fallback)

Usage:
  python convert.py --file <input_path> [--engine kreuzberg|docling|pandoc]
  python convert.py --formats
  python convert.py --engines
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

try:
    import kreuzberg as _kreuzberg

    _HAS_KREUZBERG = True
except ImportError:
    _HAS_KREUZBERG = False

try:
    from docling.document_converter import DocumentConverter as _DocumentConverter

    _HAS_DOCLING = True
except ImportError:
    _HAS_DOCLING = False

_HAS_PANDOC = shutil.which("pandoc") is not None

SUPPORTED_FORMATS: dict[str, list[str]] = {
    ".pdf": ["kreuzberg", "docling"],
    ".docx": ["kreuzberg", "docling", "pandoc"],
    ".pptx": ["kreuzberg", "docling"],
    ".xlsx": ["kreuzberg", "docling"],
    ".html": ["kreuzberg", "docling", "pandoc"],
    ".htm": ["kreuzberg", "docling", "pandoc"],
    ".png": ["kreuzberg", "docling"],
    ".jpg": ["kreuzberg", "docling"],
    ".jpeg": ["kreuzberg", "docling"],
    ".tiff": ["kreuzberg", "docling"],
    ".tif": ["kreuzberg", "docling"],
    ".epub": ["pandoc"],
    ".md": ["passthrough"],
    ".txt": ["passthrough"],
    ".rst": ["passthrough"],
}

_ENGINE_AVAILABLE = {
    "kreuzberg": _HAS_KREUZBERG,
    "docling": _HAS_DOCLING,
    "pandoc": _HAS_PANDOC,
    "passthrough": True,
}

_PANDOC_INPUT_FORMATS = {
    ".docx": "docx",
    ".html": "html",
    ".htm": "html",
    ".epub": "epub",
}


def detect_engine(ext: str, explicit: str | None = None) -> str | None:
    ext = ext.lower()
    if ext not in SUPPORTED_FORMATS:
        return None

    if explicit:
        if explicit in SUPPORTED_FORMATS[ext] and _ENGINE_AVAILABLE.get(explicit, False):
            return explicit
        return None

    for engine in SUPPORTED_FORMATS[ext]:
        if _ENGINE_AVAILABLE.get(engine, False):
            return engine
    return None


def _convert_kreuzberg(path: str) -> str:
    import asyncio

    async def _extract():
        result = await _kreuzberg.extract_file(path)
        return result.content

    return asyncio.run(_extract())


def _convert_docling(path: str) -> str:
    converter = _DocumentConverter()
    result = converter.convert(path)
    return result.document.export_to_markdown()


def _convert_pandoc(path: str, ext: str) -> str:
    input_fmt = _PANDOC_INPUT_FORMATS.get(ext)
    if not input_fmt:
        raise ValueError(f"Pandoc does not support {ext}")
    result = subprocess.run(
        ["pandoc", "-f", input_fmt, "-t", "markdown", path],
        capture_output=True, text=True, check=True,
    )
    return result.stdout


def convert_file(path: str, engine: str | None = None) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {ext}")

    selected = detect_engine(ext, explicit=engine)
    if selected is None:
        available = SUPPORTED_FORMATS[ext]
        raise RuntimeError(
            f"No conversion engine available for {ext}. "
            f"Supported engines: {', '.join(available)}. "
            f"Install one: pip install kreuzberg>=4.9"
        )

    if selected == "passthrough":
        with open(path, encoding="utf-8") as f:
            return f.read()
    elif selected == "kreuzberg":
        return _convert_kreuzberg(path)
    elif selected == "docling":
        return _convert_docling(path)
    elif selected == "pandoc":
        return _convert_pandoc(path, ext)
    else:
        raise RuntimeError(f"Unknown engine: {selected}")


def cmd_formats():
    print("Supported formats:")
    for ext, engines in sorted(SUPPORTED_FORMATS.items()):
        status = []
        for e in engines:
            if e == "passthrough":
                status.append("passthrough")
            elif _ENGINE_AVAILABLE.get(e, False):
                status.append(f"{e} (installed)")
            else:
                status.append(f"{e} (not installed)")
        print(f"  {ext:8s}  {', '.join(status)}")


def cmd_engines():
    print("Conversion engines:")
    engines = [
        ("kreuzberg", _HAS_KREUZBERG, "pip install kreuzberg>=4.9"),
        ("docling", _HAS_DOCLING, "pip install docling"),
        ("pandoc", _HAS_PANDOC, "brew/apt/winget install pandoc"),
    ]
    for name, available, install in engines:
        marker = "installed" if available else f"not installed ({install})"
        print(f"  {name:12s}  {marker}")


def main():
    parser = argparse.ArgumentParser(description="Convert documents to markdown")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="File to convert")
    group.add_argument("--formats", action="store_true", help="List supported formats")
    group.add_argument("--engines", action="store_true", help="Show installed engines")
    parser.add_argument("--engine", choices=["kreuzberg", "docling", "pandoc"],
                        help="Force a specific engine")

    args = parser.parse_args()

    if args.formats:
        cmd_formats()
        return
    if args.engines:
        cmd_engines()
        return

    try:
        result = convert_file(args.file, engine=args.engine)
        print(result)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2 if "No conversion engine" in str(e) else 1)


if __name__ == "__main__":
    main()
