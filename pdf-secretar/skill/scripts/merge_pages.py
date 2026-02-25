#!/usr/bin/env python3
"""
Merge multiple PDFs into one file with specified ordering.
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

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

def get_files(input_pattern, order):
    """Get list of PDF files according to ordering."""
    from glob import glob
    files = sorted(glob(input_pattern))
    if not files:
        print(f"No files match pattern: {input_pattern}", file=sys.stderr)
        sys.exit(1)

    if order == "name":
        # Already sorted by name
        pass
    elif order == "date":
        files.sort(key=lambda f: Path(f).stat().st_mtime)
    elif order == "list":
        # Read list from stdin or use order from arg (list of paths)
        # For simplicity, here we accept order as comma-separated basenames
        # In practice would read from file provided with --list-file
        pass
    else:
        print(f"Unknown order: {order}", file=sys.stderr)
        sys.exit(1)
    return files

def merge_pdfs(file_list, output_path):
    from PyPDF2 import PdfReader, PdfWriter

    writer = PdfWriter()
    total_pages = 0
    for pdf_file in file_list:
        with open(pdf_file, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                writer.add_page(page)
                total_pages += 1
        print(f"Added: {pdf_file} ({len(reader.pages)} pages)")

    with open(output_path, 'wb') as out_f:
        writer.write(out_f)
    print(f"Merged {len(file_list)} files, {total_pages} pages total -> {output_path}")

if __name__ == "__main__":
    add_workspace_to_path()
    if not ensure_pypdf2():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Merge PDFs with ordering")
    parser.add_argument("input_pattern", help="Input pattern, e.g., 'pages/*.pdf'")
    parser.add_argument("--output", "-o", default="merged.pdf", help="Output PDF file")
    parser.add_argument("--order", choices=["name", "date", "list"], default="name",
                        help="Sorting order: name (lexicographic), date (creation time), list (read from --list-file)")
    parser.add_argument("--list-file", help="File containing list of PDF paths in desired order (one per line)")
    args = parser.parse_args()

    if args.order == "list" and args.list_file:
        with open(args.list_file) as f:
            file_list = [line.strip() for line in f if line.strip()]
    else:
        file_list = get_files(args.input_pattern, args.order)

    merge_pdfs(file_list, args.output)
