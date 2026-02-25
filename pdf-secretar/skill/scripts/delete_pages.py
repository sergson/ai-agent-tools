#!/usr/bin/env python3
"""
Delete specific pages from a PDF.
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

def parse_pages(pages_arg):
    """Parse '2,4,6-9' into set of page numbers (1-indexed)."""
    pages = set()
    for part in pages_arg.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end+1))
        else:
            pages.add(int(part))
    return pages

def delete_pages(input_pdf, output_pdf, pages_to_delete):
    from PyPDF2 import PdfReader, PdfWriter

    input_path = Path(input_pdf)
    f_in = open(input_path, 'rb')
    try:
        reader = PdfReader(f_in)
        total = len(reader.pages)

        writer = PdfWriter()
        kept = 0
        for i in range(1, total+1):
            if i not in pages_to_delete:
                writer.add_page(reader.pages[i-1])
                kept += 1
            else:
                print(f"Deleted page {i}")

        with open(output_pdf, 'wb') as f_out:
            writer.write(f_out)
        print(f"Kept {kept} of {total} pages -> {output_pdf}")
    finally:
        f_in.close()

if __name__ == "__main__":
    add_workspace_to_path()
    if not ensure_pypdf2():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Delete pages from PDF")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("--output", "-o", default="deleted.pdf", help="Output PDF file")
    parser.add_argument("--pages", required=True, help="Pages to delete, e.g., '2,4,6-9'")
    args = parser.parse_args()

    pages_to_delete = parse_pages(args.pages)
    delete_pages(args.input_pdf, args.output, pages_to_delete)
