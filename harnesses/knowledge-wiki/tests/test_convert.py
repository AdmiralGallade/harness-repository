"""Unit tests for convert.py document-to-markdown conversion."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from convert import (
    SUPPORTED_FORMATS,
    _HAS_DOCLING,
    _HAS_KREUZBERG,
    _HAS_PANDOC,
    convert_file,
    detect_engine,
)


class TestDetectEngine:
    def test_passthrough_formats(self):
        for ext in (".md", ".txt", ".rst"):
            assert detect_engine(ext) == "passthrough"

    def test_unsupported_format(self):
        assert detect_engine(".xyz") is None

    def test_explicit_engine_override_available(self):
        if _HAS_KREUZBERG:
            assert detect_engine(".pdf", explicit="kreuzberg") == "kreuzberg"
        elif _HAS_DOCLING:
            assert detect_engine(".pdf", explicit="docling") == "docling"
        elif _HAS_PANDOC:
            assert detect_engine(".docx", explicit="pandoc") == "pandoc"
        else:
            pytest.skip("no conversion engine installed")

    def test_explicit_engine_unavailable(self):
        if not _HAS_DOCLING:
            assert detect_engine(".pdf", explicit="docling") is None

    def test_explicit_engine_invalid_for_format(self):
        assert detect_engine(".pdf", explicit="pandoc") is None

    def test_pdf_needs_kreuzberg_or_docling(self):
        engine = detect_engine(".pdf")
        if _HAS_KREUZBERG:
            assert engine == "kreuzberg"
        elif _HAS_DOCLING:
            assert engine == "docling"
        else:
            assert engine is None

    def test_docx_fallback_chain(self):
        engine = detect_engine(".docx")
        if _HAS_KREUZBERG:
            assert engine == "kreuzberg"
        elif _HAS_DOCLING:
            assert engine == "docling"
        elif _HAS_PANDOC:
            assert engine == "pandoc"
        else:
            assert engine is None


class TestSupportedFormats:
    def test_pdf_in_formats(self):
        assert ".pdf" in SUPPORTED_FORMATS

    def test_docx_in_formats(self):
        assert ".docx" in SUPPORTED_FORMATS

    def test_passthrough_in_formats(self):
        assert ".md" in SUPPORTED_FORMATS
        assert ".txt" in SUPPORTED_FORMATS

    def test_format_values_are_lists(self):
        for ext, engines in SUPPORTED_FORMATS.items():
            assert isinstance(engines, list), f"{ext} value is not a list"


class TestPassthrough:
    def test_md_passthrough(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Hello\n\nBody text.")
        result = convert_file(str(f))
        assert result == "# Hello\n\nBody text."

    def test_txt_passthrough(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Plain text content.")
        result = convert_file(str(f))
        assert result == "Plain text content."

    def test_rst_passthrough(self, tmp_path):
        f = tmp_path / "test.rst"
        f.write_text("Title\n=====\n\nParagraph.")
        result = convert_file(str(f))
        assert result == "Title\n=====\n\nParagraph."


class TestErrorHandling:
    def test_unsupported_format_raises(self, tmp_path):
        f = tmp_path / "test.xyz"
        f.write_text("data")
        with pytest.raises(ValueError, match="Unsupported format"):
            convert_file(str(f))

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            convert_file("/nonexistent/file.pdf")

    def test_no_engine_for_format(self, tmp_path):
        f = tmp_path / "test.pdf"
        f.write_text("fake pdf")
        if not _HAS_KREUZBERG and not _HAS_DOCLING:
            with pytest.raises(RuntimeError, match="No conversion engine"):
                convert_file(str(f))


_CONVERT_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "skills", "wiki-index", "convert.py"
)


class TestCLI:
    def test_formats_subcommand(self):
        result = subprocess.run(
            [sys.executable, _CONVERT_SCRIPT, "--formats"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert ".pdf" in result.stdout
        assert ".docx" in result.stdout

    def test_engines_subcommand(self):
        result = subprocess.run(
            [sys.executable, _CONVERT_SCRIPT, "--engines"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "kreuzberg" in result.stdout.lower()


@pytest.mark.skipif(not _HAS_KREUZBERG, reason="kreuzberg not installed")
class TestKreuzbergIntegration:
    def test_convert_txt_via_kreuzberg(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Kreuzberg test content.")
        result = convert_file(str(f), engine="kreuzberg")
        assert "Kreuzberg test content" in result
