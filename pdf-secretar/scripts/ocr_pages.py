#!/usr/bin/env python3
"""
OCR pages: extract text from pages (via PyPDF2 or optional pytesseract) and save to text file.
Optionally create searchable PDF with text layer (requires additional libs).
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
    """Parse '1-3,5' into list of 0-indexed page numbers."""
    if not pages_arg:
        return list(range(total))
    pages = set()
    for part in pages_arg.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start-1, end))  # to 0-index
        else:
            pages.add(int(part)-1)
    return sorted(p for p in pages if 0 <= p < total)

def extract_text_pypdf2(pdf_path, pages_list):
    from PyPDF2 import PdfReader
    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)
        texts = {}
        for p in pages_list:
            if p < len(reader.pages):
                text = reader.pages[p].extract_text() or ""
                texts[p] = text
            else:
                texts[p] = ""
        return texts

def extract_text_ocr(pdf_path, pages_list):
    """Optional OCR via pytesseract and pdf2image (if installed)."""
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError:
        print("ERROR: ДляOCR установите: uv pip install pytesseract pdf2image pillow", file=sys.stderr)
        sys.exit(1)

    images = convert_from_path(pdf_path, first_page=min(pages_list)+1, last_page=max(pages_list)+1)
    texts = {}
    for idx, p in enumerate(pages_list):
        if idx < len(images):
            text = pytesseract.image_to_string(images[idx])
            texts[p] = text
        else:
            texts[p] = ""
    return texts

def write_text_file(texts, output_txt):
    with open(output_txt, 'w', encoding='utf-8') as f:
        for page_num in sorted(texts.keys()):
            f.write(f"=== Page {page_num+1} ===\n")
            f.write(texts[page_num].strip())
            f.write("\n\n")
    print(f"Text extracted to {output_txt}")

def ocr_pages(input_pdf, pages_arg, text_output, use_ocr):
    from PyPDF2 import PdfReader

    input_path = Path(input_pdf)
    with open(input_path, 'rb') as f:
        reader = PdfReader(f)
        total = len(reader.pages)

    pages_to_process = parse_pages(pages_arg, total)

    if use_ocr:
        texts = extract_text_ocr(input_pdf, pages_to_process)
    else:
        texts = extract_text_pypdf2(input_pdf, pages_to_process)

    write_text_file(texts, text_output)
    print(f"Processed {len(pages_to_process)} pages.")

if __name__ == "__main__":
    add_workspace_to_path()
    if not ensure_pypdf2():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="OCR/extract text from PDF pages")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("--pages", help="Pages to process, e.g., '1-3,5' (default: all)")
    parser.add_argument("--text-output", "-t", default="extracted.txt", help="Output text file")
    parser.add_argument("--ocr", action="store_true", help="Use OCR (requires pytesseract, pdf2image)")
    args = parser.parse_args()

    ocr_pages(args.input_pdf, args.pages, args.text_output, args.ocr)
