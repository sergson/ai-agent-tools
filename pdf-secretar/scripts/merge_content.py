#!/usr/bin/env python3
"""
Merge PDFs by content-based ordering: search each file for patterns and sort by match.
"""
import sys
import argparse
import re
from pathlib import Path

def add_workspace_to_path():
    ws = Path.home() / ".openclaw" / "workspace"
    venv = ws / ".venv" / "lib" / "python3.12" / "site-packages"
    if venv.exists():
        sys.path.insert(0, str(venv))

def ensure_pypdf2():
    try:
        import PyPDF2  # noqa: F401
        return True
    except ImportError:
        print("ERROR: PyPDF2 не установлен. Установите: uv pip install PyPDF2", file=sys.stderr)
        return False

def extract_text(pdf_path):
    from PyPDF2 import PdfReader
    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)
        return " ".join(page.extract_text() or "" for page in reader.pages)

def find_pattern_index(text, patterns):
    """Return index of first pattern found in text (case-insensitive), or len(patterns) if none."""
    text_lower = text.lower()
    for idx, pat in enumerate(patterns):
        if re.search(pat, text_lower, re.IGNORECASE):
            return idx
    return len(patterns)

def merge_content(input_pattern, patterns, output):
    from glob import glob
    files = sorted(glob(input_pattern))
    if not files:
        print(f"No files match pattern: {input_pattern}", file=sys.stderr)
        sys.exit(1)

    # Compute sort key for each file
    file_scores = []
    for f in files:
        text = extract_text(f)
        score = find_pattern_index(text, patterns)
        file_scores.append((f, score))

    # Sort by score (lower is better)
    file_scores.sort(key=lambda x: x[1])
    sorted_files = [f for f, _ in file_scores]

    # Merge
    from PyPDF2 import PdfReader, PdfWriter
    writer = PdfWriter()
    total_pages = 0
    for pdf_file in sorted_files:
        with open(pdf_file, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                writer.add_page(page)
                total_pages += 1
        print(f"Added: {pdf_file} ({len(reader.pages)} pages, pattern index: {file_scores[sorted_files.index(pdf_file)][1]})")

    with open(output, 'wb') as out_f:
        writer.write(out_f)
    print(f"Merged {len(sorted_files)} files, {total_pages} pages -> {output}")

if __name__ == "__main__":
    add_workspace_to_path()
    if not ensure_pypdf2():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Merge PDFs by content pattern ordering")
    parser.add_argument("input_pattern", help="Input pattern, e.g., 'docs/*.pdf'")
    parser.add_argument("--patterns", required=True,
                        help="Comma-separated patterns to search (in order). Files matching earlier patterns come first. Example: 'договор,акт,счёт'")
    parser.add_argument("--output", "-o", default="merged_content.pdf", help="Output PDF file")
    args = parser.parse_args()

    patterns = [p.strip() for p in args.patterns.split(',') if p.strip()]
    if not patterns:
        print("No patterns provided", file=sys.stderr)
        sys.exit(1)

    merge_content(args.input_pattern, patterns, args.output)
