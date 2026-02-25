#!/usr/bin/env python3
"""
Extract PDF pages as image files (PNG/JPEG).
"""
import sys
import argparse
from pathlib import Path

def add_workspace_to_path():
    ws = Path.home() / ".openclaw" / "workspace"
    venv = ws / ".venv" / "lib" / "python3.12" / "site-packages"
    if venv.exists():
        sys.path.insert(0, str(venv))

def ensure_pdf2image():
    try:
        import pdf2image  # noqa: F401
        from PIL import Image  # noqa: F401
        return True
    except ImportError:
        print("ERROR: Установите: uv pip install pdf2image pillow", file=sys.stderr)
        return False

def parse_pages(pages_arg, total):
    if not pages_arg:
        return list(range(total))
    pages = set()
    for part in pages_arg.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            # pdf2image uses 1-indexed pages in first_page/last_page
            pages.update(range(start, end+1))
        else:
            pages.add(int(part))
    # Filter valid
    return sorted(p for p in pages if 1 <= p <= total)

def extract_images(pdf_path, output_dir, img_format, dpi, pages_arg):
    from pdf2image import convert_from_path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get total page count quickly
    from PyPDF2 import PdfReader
    with open(pdf_path, 'rb') as f:
        total = len(PdfReader(f).pages)

    pages_to_extract = parse_pages(pages_arg, total)
    if not pages_to_extract:
        print("No pages to extract", file=sys.stderr)
        return

    first = min(pages_to_extract)
    last = max(pages_to_extract)

    print(f"Converting pages {first}-{last} to {img_format.upper()} at {dpi} DPI...")
    images = convert_from_path(pdf_path, dpi=dpi, first_page=first, last_page=last, fmt=img_format)

    # Map extracted images back to requested page numbers
    for idx, page_num in enumerate(range(first, last+1)):
        if page_num in pages_to_extract:
            img = images[idx]
            out_file = output_dir / f"page_{page_num:03d}.{img_format}"
            img.save(out_file, format=img_format.upper())
            print(f"Saved: {out_file.name}")

    print(f"Extracted {len(pages_to_extract)} images.")

if __name__ == "__main__":
    add_workspace_to_path()
    if not ensure_pdf2image():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Extract PDF pages as PNG/JPEG images")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("--output-dir", "-o", default="pages_images", help="Output directory")
    parser.add_argument("--format", choices=["png", "jpeg"], default="png", help="Image format")
    parser.add_argument("--dpi", type=int, default=200, help="Resolution in DPI")
    parser.add_argument("--pages", help="Pages to extract, e.g., '1-3,5' (default: all)")
    args = parser.parse_args()

    extract_images(args.input_pdf, args.output_dir, args.format, args.dpi, args.pages)
