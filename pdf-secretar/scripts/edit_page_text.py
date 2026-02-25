#!/usr/bin/env python3
"""
Edit text on a specific page using nano-pdf.
"""
import sys
import argparse
import subprocess
from pathlib import Path

def add_workspace_to_path():
    ws = Path.home() / ".openclaw" / "workspace"
    venv = ws / ".venv" / "lib" / "python3.12" / "site-packages"
    if venv.exists():
        sys.path.insert(0, str(venv))

def edit_page_text(input_pdf, page_num, instruction, output_pdf):
    """Run nano-pdf edit command."""
    # nano-pdf expects 0-based page numbers
    zero_based = page_num - 1
    cmd = ["nano-pdf", "edit", str(input_pdf), str(zero_based), instruction, "--output", str(output_pdf)]
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Edited page {page_num} -> {output_pdf}")
    except subprocess.CalledProcessError as e:
        print(f"nano-pdf failed: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: nano-pdf command not found. Install nano-pdf skill first.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    add_workspace_to_path()

    parser = argparse.ArgumentParser(description="Edit text on a PDF page using nano-pdf")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("--page", type=int, required=True, help="Page number to edit (1-indexed)")
    parser.add_argument("--instruction", required=True, help="Edit instruction in natural language")
    parser.add_argument("--output", "-o", default="edited.pdf", help="Output PDF file")
    args = parser.parse_args()

    if args.page < 1:
        print("Page number must be >= 1", file=sys.stderr)
        sys.exit(1)

    edit_page_text(args.input_pdf, args.page, args.instruction, args.output)
