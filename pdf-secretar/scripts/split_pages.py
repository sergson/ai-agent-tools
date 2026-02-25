#!/usr/bin/env python3
"""
Split PDF into separate pages or page ranges.
"""
import sys
import argparse
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

def parse_ranges(ranges_str):
    """Parse '1-3,5,7-9' into list of page numbers (1-indexed)."""
    pages = set()
    for part in ranges_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end+1))
        else:
            pages.add(int(part))
    return sorted(pages)

def split_pdf(input_pdf, output_dir, ranges):
    from PyPDF2 import PdfReader, PdfWriter

    input_path = Path(input_pdf)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Open file once and keep reference to avoid closed file issue
    f = open(input_path, 'rb')
    reader = PdfReader(f)
    total_pages = len(reader.pages)

    if not ranges:
        ranges = list(range(1, total_pages+1))

    try:
        for page_num in ranges:
            if page_num < 1 or page_num > total_pages:
                print(f"Warning: page {page_num} out of range (1-{total_pages}), skipping", file=sys.stderr)
                continue
            writer = PdfWriter()
            # Add page directly from reader (reader stays open)
            writer.add_page(reader.pages[page_num-1])
            out_file = output_dir / f"page_{page_num:03d}.pdf"
            with open(out_file, 'wb') as out_f:
                writer.write(out_f)
            print(f"Created: {out_file.name}")
    finally:
        f.close()

    print(f"Split {len(ranges)} pages from {total_pages} total.")

if __name__ == "__main__":
    add_workspace_to_path()
    if not ensure_pypdf2():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Split PDF by page ranges")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("--output-dir", "-o", default="pages", help="Output directory (default: pages)")
    parser.add_argument("--ranges", help="Page ranges, e.g., '1-3,5,7-9' (default: all pages)")
    args = parser.parse_args()

    ranges = parse_ranges(args.ranges) if args.ranges else None
    split_pdf(args.input_pdf, args.output_dir, ranges)
