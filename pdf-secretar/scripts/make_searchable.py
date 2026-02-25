#!/usr/bin/env python3
"""
Make PDF searchable: add OCR text layer to scanned PDF or image.
Requires system dependencies: ghostscript, tesseract, pdftoppm (poppler).
"""
import sys
import argparse
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required binaries are available."""
    missing = []
    for bin in ['gs', 'tesseract', 'pdftoppm']:
        if not subprocess.run(['which', bin], capture_output=True).returncode == 0:
            missing.append(bin)
    return missing

def get_venv_python():
    """Return path to Python in workspace venv."""
    ws = Path.home() / ".openclaw" / "workspace"
    venv_python = ws / ".venv" / "bin" / "python"
    if not venv_python.exists():
        print(f"ERROR: Workspace venv python not found at {venv_python}", file=sys.stderr)
        sys.exit(1)
    return str(venv_python)

def make_searchable(input_pdf, output_pdf, lang='rus+eng', extra_args=None, **kwargs):
    """
    Run ocrmypdf to create searchable PDF using workspace venv python.
    """
    missing = check_dependencies()
    if missing:
        print(f"ERROR: Missing system dependencies: {', '.join(missing)}", file=sys.stderr)
        print("Install them (Ubuntu/Debian):", file=sys.stderr)
        print("  sudo apt-get install ghostscript tesseract-ocr poppler-utils", file=sys.stderr)
        sys.exit(1)

    venv_python = get_venv_python()

    args = [venv_python, '-m', 'ocrmypdf', input_pdf, output_pdf, '--language', lang]

    # Add standard flags
    if kwargs.get('deskew'):
        args.append('--deskew')
    if kwargs.get('clean'):
        args.append('--clean')
    if kwargs.get('optimize'):
        args.extend(['--optimize', str(kwargs['optimize'])])
    if kwargs.get('output_type'):
        args.extend(['--output-type', kwargs['output_type']])

    # Append any extra arguments passed through
    if extra_args:
        args.extend(extra_args)

    print(f"Running: {' '.join(args)}")
    try:
        subprocess.run(args, check=True)
        print(f"Searchable PDF created: {output_pdf}")
    except subprocess.CalledProcessError as e:
        print(f"ocrmypdf failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create searchable PDF from scanned document using OCR",
        epilog="Extra arguments (after '--') are passed directly to ocrmypdf. See: ocrmypdf --help"
    )
    parser.add_argument("input_pdf", help="Input scanned PDF or image-based PDF")
    parser.add_argument("--output", "-o", default="searchable.pdf", help="Output PDF file")
    parser.add_argument("--lang", default="rus+eng", help="OCR languages (e.g., 'eng+rus', 'rus')")
    parser.add_argument("--deskew", action='store_true', help="Deskew pages before OCR")
    parser.add_argument("--clean", action='store_true', help="Clean pages before OCR")
    parser.add_argument("--optimize", type=int, help="PDF optimization level (0-3)")
    parser.add_argument("--output-type", choices=['pdf', 'pdfa', 'pdfa-1', 'pdfa-2', 'pdfa-3'], help="Output PDF type")
    # Parse known args and extra
    args, extra = parser.parse_known_args()

    make_searchable(
        args.input_pdf,
        args.output,
        lang=args.lang,
        deskew=args.deskew,
        clean=args.clean,
        optimize=args.optimize,
        output_type=args.output_type,
        extra_args=extra if extra else None
    )
