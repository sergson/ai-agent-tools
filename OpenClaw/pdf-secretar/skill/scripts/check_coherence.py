#!/usr/bin/env python3
"""
Check logical coherence between consecutive pages by comparing text overlap.
"""
import sys
import argparse
from pathlib import Path
import re

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

def extract_text(pdf_path):
    from PyPDF2 import PdfReader
    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return texts

def sentence_boundaries(text):
    """Split text into sentences (simple)."""
    # Split by . ! ? followed by space or newline, keep delimiters
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def check_coherence(texts, threshold=0.3):
    """
    Compare sentences between consecutive pages.
    Returns dict with page i -> score (fraction of sentence overlap).
    Lower score indicates possible break.
    """
    results = {}
    for i in range(len(texts)-1):
        s1 = set(sentence_boundaries(texts[i]))
        s2 = set(sentence_boundaries(texts[i+1]))
        if not s1 or not s2:
            results[i+1] = 0.0
            continue
        overlap = len(s1 & s2)
        # Normalize by smaller set to detect missing context
        score = overlap / min(len(s1), len(s2))
        results[i+1] = score
    return results

def main():
    add_workspace_to_path()
    if not ensure_pypdf2():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Check coherence between consecutive pages")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("--threshold", type=float, default=0.3,
                        help="Threshold below which page break is suspicious (0.0-1.0)")
    parser.add_argument("--output", "-o", help="Optional report file")
    args = parser.parse_args()

    texts = extract_text(args.input_pdf)
    coherence = check_coherence(texts, args.threshold)

    print(f"Coherence check for {args.input_pdf} ({len(texts)} pages):")
    for page_num, score in coherence.items():
        status = "OK" if score >= args.threshold else "LOW"
        print(f"  Page {page_num} -> {page_num+1}: {score:.2f} [{status}]")

    if args.output:
        with open(args.output, 'w') as f:
            f.write(f"Coherence report: {args.input_pdf}\n")
            for page_num, score in coherence.items():
                f.write(f"{page_num},{score:.3f},{'OK' if score>=args.threshold else 'LOW'}\n")
        print(f"Report saved to {args.output}")

if __name__ == "__main__":
    main()
