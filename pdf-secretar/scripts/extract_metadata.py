#!/usr/bin/env python3
"""
Extract PDF metadata (title, author, dates, etc.) and output as JSON.
"""
import sys
import argparse
import json
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

def extract_metadata(pdf_path):
    from PyPDF2 import PdfReader
    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)
        meta = reader.metadata
        # Convert to plain dict; keys often like '/Title'
        data = {}
        for key in ['/Title', '/Author', '/Subject', '/Creator', '/Producer', '/CreationDate', '/ModDate']:
            value = meta.get(key)
            if value:
                # Clean leading slash for JSON convenience
                data[key.lstrip('/').lower()] = str(value)
            else:
                data[key.lstrip('/').lower()] = None
        data['pages'] = len(reader.pages)
        return data

if __name__ == "__main__":
    add_workspace_to_path()
    if not ensure_pypdf2():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Extract PDF metadata as JSON")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("--output", "-o", help="Write JSON to file instead of stdout")
    args = parser.parse_args()

    data = extract_metadata(args.input_pdf)
    json_str = json.dumps(data, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"Metadata saved to {args.output}")
    else:
        print(json_str)
