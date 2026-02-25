#!/usr/bin/env python3
"""
Sort/reorder pages within a PDF: move page from position X to Y.
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

def parse_moves(moves_arg):
    """Parse '5:2,8:5' into list of (src, dst) tuples (1-indexed)."""
    moves = []
    for part in moves_arg.split(','):
        part = part.strip()
        if ':' not in part:
            print(f"Invalid move spec: {part}, expected FROM:TO", file=sys.stderr)
            sys.exit(1)
        src, dst = map(int, part.split(':'))
        moves.append((src, dst))
    return moves

def apply_moves(pages, moves):
    """Apply moves in order (from first to last). Each move inserts src page at dst position."""
    total = len(pages)
    for src, dst in moves:
        if src < 1 or src > total:
            print(f"Invalid source page {src} (valid: 1-{total})", file=sys.stderr)
            sys.exit(1)
        if dst < 1 or dst > total + 1:
            print(f"Invalid destination {dst} (valid: 1-{total+1})", file=sys.stderr)
            sys.exit(1)
        # Extract page (1-indexed to 0-index)
        page = pages.pop(src-1)
        # Insert at destination (1-indexed to 0-index)
        pages.insert(dst-1, page)
    return pages

def sort_pages(input_pdf, output_pdf, moves):
    from PyPDF2 import PdfReader, PdfWriter

    input_path = Path(input_pdf)
    f = open(input_path, 'rb')
    try:
        reader = PdfReader(f)
        # Get pages list while file open
        pages = list(reader.pages)

        new_pages = apply_moves(pages[:], moves)

        writer = PdfWriter()
        for page in new_pages:
            writer.add_page(page)

        with open(output_pdf, 'wb') as out_f:
            writer.write(out_f)
        print(f"Sorted {len(moves)} moves, {len(new_pages)} pages -> {output_pdf}")
    finally:
        f.close()

if __name__ == "__main__":
    add_workspace_to_path()
    if not ensure_pypdf2():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Sort/reorder pages within PDF")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("--output", "-o", default="sorted.pdf", help="Output PDF file")
    parser.add_argument("--move", required=True, help="Moves: 'FROM:TO' comma-separated, e.g., '5:2,8:5'")
    args = parser.parse_args()

    moves = parse_moves(args.move)
    sort_pages(args.input_pdf, args.output, moves)
