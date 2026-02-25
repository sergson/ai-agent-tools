#!/usr/bin/env python3
"""
OCR pages: extract text from PDF pages with different quality presets.
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

def ensure_pypdf2():
    try:
        import PyPDF2  # noqa: F401
        return True
    except ImportError:
        print("ERROR: PyPDF2 не установлен. Установите: uv pip install PyPDF2", file=sys.stderr)
        return False

def ensure_ocr_deps():
    try:
        import pdf2image  # noqa: F401
        from PIL import Image  # noqa: F401
        import pytesseract  # noqa: F401
        return True
    except ImportError:
        print("ERROR: ДляOCR установите: uv pip install pytesseract pdf2image pillow", file=sys.stderr)
        return False

def check_ocrmypdf():
    try:
        import ocrmypdf  # noqa: F401
        return True
    except ImportError:
        return False

def get_venv_python():
    ws = Path.home() / ".openclaw" / "workspace"
    venv_python = ws / ".venv" / "bin" / "python"
    if not venv_python.exists():
        print(f"ERROR: Workspace venv python not found at {venv_python}", file=sys.stderr)
        sys.exit(1)
    return str(venv_python)

def parse_pages(pages_arg, total):
    """Parse '1-3,5' into list of 1-indexed page numbers."""
    if not pages_arg:
        return None
    pages = set()
    for part in pages_arg.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end+1))
        else:
            pages.add(int(part))
    # Validate
    pages = {p for p in pages if 1 <= p <= total}
    return sorted(pages) if pages else None

def ocr_via_ocrmypdf(input_pdf, output_txt, pages=None):
    """
    Use ocrmypdf with 'dark' preset parameters, output text to sidecar.
    """
    if not check_ocrmypdf():
        print("ERROR: ocrmypdf not installed. Run: uv pip install ocrmypdf", file=sys.stderr)
        sys.exit(1)

    venv_python = get_venv_python()

    # Get total pages to validate page numbers
    from PyPDF2 import PdfReader
    with open(input_pdf, 'rb') as f:
        total = len(PdfReader(f).pages)

    pages_ocrmypdf = parse_pages(pages, total) if pages else None

    args = [venv_python, '-m', 'ocrmypdf', input_pdf, '/dev/null', '--sidecar', output_txt, '--language', 'rus+eng']
    if pages_ocrmypdf:
        args.extend(['--pages', ','.join(map(str, pages_ocrmypdf))])
    args.extend(['--deskew', '--image-dpi', '300', '--tesseract-thresholding', 'adaptive-otsu', '--rotate-pages'])

    print(f"Running ocrmypdf (dark preset): {' '.join(args)}")
    try:
        subprocess.run(args, check=True)
        print(f"Text extracted via ocrmypdf to {output_txt}")
    except subprocess.CalledProcessError as e:
        print(f"ocrmypdf failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(1)

def ocr_via_pytesseract(input_pdf, output_txt, pages_arg, dpi=200):
    """Ordinary OCR via pdf2image + pytesseract."""
    from PyPDF2 import PdfReader
    from pdf2image import convert_from_path
    import pytesseract

    input_path = Path(input_pdf)
    with open(input_path, 'rb') as f:
        reader = PdfReader(f)
        total = len(reader.pages)

    # Parse pages to 0-indexed
    if not pages_arg:
        pages_list = list(range(total))
    else:
        pages = set()
        for part in pages_arg.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                pages.update(range(start-1, end))
            else:
                pages.add(int(part)-1)
        pages_list = sorted(p for p in pages if 0 <= p < total)

    if not pages_list:
        print("No valid pages to process", file=sys.stderr)
        sys.exit(1)

    first_page = min(pages_list) + 1
    last_page = max(pages_list) + 1
    images = convert_from_path(input_pdf, first_page=first_page, last_page=last_page, dpi=dpi)

    lang = 'rus+eng'
    custom_config = '--oem 3 --psm 3'

    texts = {}
    for idx, p in enumerate(pages_list):
        if idx < len(images):
            text = pytesseract.image_to_string(images[idx], lang=lang, config=custom_config)
            texts[p] = text
        else:
            texts[p] = ""

    with open(output_txt, 'w', encoding='utf-8') as f:
        for page_num in sorted(texts.keys()):
            f.write(f"=== Page {page_num+1} ===\n")
            f.write(texts[page_num].strip())
            f.write("\n\n")
    print(f"Text extracted to {output_txt} (pytesseract, DPI={dpi})")

def main():
    add_workspace_to_path()
    if not ensure_pypdf2():
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Extract text from PDF pages using OCR with quality presets",
        epilog="Presets: 'default' = ordinary OCR (pytesseract, DPI 200), 'dark' = advanced OCR for dark/noisy scans (ocrmypdf with preprocessing)."
    )
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("--pages", help="Pages to process, e.g., '1-3,5' (default: all)")
    parser.add_argument("--text-output", "-t", default="extracted.txt", help="Output text file")
    parser.add_argument("--preset", choices=['default', 'dark'], default='default',
                        help="Quality preset: 'default' = normal OCR (pytesseract), 'dark' = advanced OCR for difficult scans")
    args = parser.parse_args()

    if args.preset == 'default':
        # Ordinary OCR via pytesseract
        if not ensure_ocr_deps():
            sys.exit(1)
        ocr_via_pytesseract(args.input_pdf, args.text_output, args.pages, dpi=200)
    elif args.preset == 'dark':
        # Advanced OCR via ocrmypdf
        ocr_via_ocrmypdf(args.input_pdf, args.text_output, pages=args.pages)
    else:
        # Should not happen due to choices
        print(f"Unknown preset: {args.preset}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
