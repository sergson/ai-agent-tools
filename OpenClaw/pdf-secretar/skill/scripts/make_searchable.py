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

def make_searchable(input_pdf, output_pdf, lang='rus+eng',
                    deskew=False, clean=False, optimize=None, output_type=None,
                    image_dpi=None, tesseract_thresholding=None, rotate_pages=False):
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

    if deskew:
        args.append('--deskew')
    if clean:
        args.append('--clean')
    if optimize is not None:
        args.extend(['--optimize', str(optimize)])
    if output_type:
        args.extend(['--output-type', output_type])
    if image_dpi:
        args.extend(['--image-dpi', str(image_dpi)])
    if tesseract_thresholding:
        args.extend(['--tesseract-thresholding', tesseract_thresholding])
    if rotate_pages:
        args.append('--rotate-pages')

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
        epilog="Use --preset to apply predefined settings for difficult images."
    )
    parser.add_argument("input_pdf", help="Input scanned PDF or image-based PDF")
    parser.add_argument("--output", "-o", default="searchable.pdf", help="Output PDF file")
    parser.add_argument("--lang", default="rus+eng", help="OCR languages (e.g., 'eng+rus', 'rus')")
    parser.add_argument("--deskew", action='store_true', help="Deskew pages before OCR")
    parser.add_argument("--clean", action='store_true', help="Clean pages before OCR (requires unpaper)")
    parser.add_argument("--optimize", type=int, help="PDF optimization level (0-3)")
    parser.add_argument("--output-type", choices=['pdf', 'pdfa', 'pdfa-1', 'pdfa-2', 'pdfa-3'], help="Output PDF type")
    parser.add_argument("--image-dpi", type=int, help="DPI for input images (if input is image)")
    parser.add_argument("--tesseract-thresholding", choices=['auto', 'otsu', 'adaptive-otsu', 'sauvola'],
                        help="Thresholding method for Tesseract")
    parser.add_argument("--rotate-pages", action='store_true', help="Auto-rotate pages")
    parser.add_argument("--preset", choices=['default', 'dark'], default='default',
                        help="Preset configuration: 'dark' for low-quality, noisy, or dark scans")
    args = parser.parse_args()

    # Apply preset overrides
    deskew = args.deskew
    clean = args.clean
    optimize = args.optimize
    output_type = args.output_type
    image_dpi = args.image_dpi
    tesseract_thresholding = args.tesseract_thresholding
    rotate_pages = args.rotate_pages

    if args.preset == 'dark':
        deskew = True
        image_dpi = 300
        tesseract_thresholding = 'adaptive-otsu'
        rotate_pages = True
        # clean remains as user-specified (requires unpaper)

    make_searchable(
        args.input_pdf,
        args.output,
        lang=args.lang,
        deskew=deskew,
        clean=clean,
        optimize=optimize,
        output_type=output_type,
        image_dpi=image_dpi,
        tesseract_thresholding=tesseract_thresholding,
        rotate_pages=rotate_pages
    )
