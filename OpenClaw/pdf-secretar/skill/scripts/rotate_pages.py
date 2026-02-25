#!/usr/bin/env python3
"""
Rotate pages in a PDF by specified degrees.
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

def parse_pages(pages_arg, total):
    if not pages_arg:
        return set()
    pages = set()
    for part in pages_arg.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end+1))
        else:
            pages.add(int(part))
    return {p for p in pages if 1 <= p <= total}

def rotate_pages(input_pdf, output_pdf, degrees, pages_arg):
    from PyPDF2 import PdfReader, PdfWriter

    input_path = Path(input_pdf)
    f_in = open(input_path, 'rb')
    try:
        reader = PdfReader(f_in)
        total = len(reader.pages)
        pages_to_rotate = parse_pages(pages_arg, total) if pages_arg else set(range(1, total+1))

        writer = PdfWriter()
        for i, page in enumerate(reader.pages, start=1):
            if i in pages_to_rotate:
                # PyPDF2 3.0+ uses .rotate() instead of .rotate_clockwise()
                if degrees in (90, 180, 270):
                    page.rotate(degrees)
                else:
                    page.rotate(degrees)
            writer.add_page(page)

        with open(output_pdf, 'wb') as f_out:
            writer.write(f_out)
        print(f"Rotated {len(pages_to_rotate)} pages by {degrees}° -> {output_pdf}")
    finally:
        f_in.close()

if __name__ == "__main__":
    add_workspace_to_path()
    if not ensure_pypdf2():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Rotate PDF pages")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("--output", "-o", default="rotated.pdf", help="Output PDF file")
    parser.add_argument("--degrees", type=int, choices=[90, 180, 270], required=True,
                        help="Rotation angle (90, 180, 270)")
    parser.add_argument("--pages", help="Pages to rotate, e.g., '1-3,5' (default: all)")
    args = parser.parse_args()

    rotate_pages(args.input_pdf, args.output, args.degrees, args.pages)
