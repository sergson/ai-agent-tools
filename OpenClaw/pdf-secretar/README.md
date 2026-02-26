# PDF Secretary Skill

**pdf-secretar** is a comprehensive toolkit for advanced PDF manipulation. It provides a set of command-line tools to split, merge, reorder, delete, edit, watermark, rotate, OCR, validate, and intelligently merge PDF documents. Designed for complex document processing beyond simple splitting or merging.

## Features

| Script | Description |
|--------|-------------|
| `split_pages.py` | Split PDF by page ranges or individual pages. |
| `merge_pages.py` | Merge multiple PDFs sorted by filename, modification date, or a custom list. |
| `merge_content.py` | Merge PDFs based on content patterns: files matching earlier patterns appear first. |
| `smart_merge.py` | **Intelligent merge** using document signatures and learned patterns. Determines logical order by content (first 300 words) with optional AI assistance (OpenRouter) and saves templates for future use. |
| `delete_pages.py` | Remove specified pages from a PDF. |
| `sort_pages.py` | Reorder pages by moving them to new positions (e.g., move page 5 to position 2). |
| `edit_page_text.py` | Edit text on a specific page using natural language instructions (requires [nano-pdf](https://github.com/your-repo/nano-pdf)). |
| `check_coherence.py` | Analyze sentence overlap between consecutive pages to detect logical breaks. |
| `ocr_pages.py` | Extract text from pages (via PyPDF2 or OCR with Tesseract). |
| `extract_images.py` | Convert PDF pages to PNG/JPEG images. |
| `add_watermark.py` | Add text or image watermark to all pages. |
| `rotate_pages.py` | Rotate pages by 90°, 180°, or 270°. |
| `extract_metadata.py` | Export PDF metadata (title, author, dates, etc.) as JSON. |
| `make_searchable.py` | Add an OCR text layer to scanned/image‑based PDFs (uses OCRmyPDF). |

---

## Installation

### System Dependencies

Some features require system tools. On Ubuntu/Debian:

    sudo apt-get install poppler-utils tesseract-ocr ghostscript

### Python Packages

Install the required Python packages (preferably in a virtual environment):

    # Core (required for all basic operations)
    uv pip install PyPDF2

    # Optional features:
    uv pip install pytesseract pdf2image pillow   # OCR and image extraction
    uv pip install reportlab                       # text watermark
    uv pip install ocrmypdf                         # make_searchable.py
    uv pip install requests                          # smart_merge.py (AI model)

### Skill Installation (OpenClaw)

If you are using OpenClaw, the skill can be installed as:

    # Copy the skill folder to ~/.npm-global/lib/node_modules/openclaw/skills/
    # or use the OpenClaw skill manager (if available).

---

## Usage

All scripts accept `--help` for detailed options. Page numbers are **1‑indexed** (first page = 1) unless noted otherwise.

### Split PDF

    python3 split_pages.py input.pdf --ranges 1-3,5,7-9 --output-dir pages/

### Merge PDFs

#### By filename or date

    python3 merge_pages.py "pages/*.pdf" --order name --output merged.pdf
    python3 merge_pages.py "pages/*.pdf" --order date --output merged.pdf

#### By a custom list

    echo "doc1.pdf
    doc3.pdf
    doc2.pdf" > list.txt
    python3 merge_pages.py "*.pdf" --order list --list-file list.txt --output merged.pdf

#### By content patterns

    python3 merge_content.py "docs/*.pdf" --patterns "договор,акт,счёт" --output merged.pdf

Patterns are matched case‑insensitively. Files containing earlier patterns appear first.

#### Intelligent merge (smart_merge.py)

This script uses **content signatures** (ordered list of meaningful words from the first ~300 words of each PDF) to determine the logical order for merging. It can:
- Match against previously saved **patterns** (templates) to reuse known document orders.
- If no pattern matches, it can ask an AI model (OpenRouter) to suggest an order (requires `OPENROUTER_API_KEY` or `OPENAI_API_KEY`).
- After user confirmation, the new order is saved as a pattern for future runs.

Basic usage:

    python3 smart_merge.py --files "docs/*.pdf" --output merged.pdf

**Options:**
- `--files`, `-f` – file mask (e.g., `"/media/temp/*.pdf"`).
- `--output` – output PDF file (default: `smart_merged.pdf`).
- `--use-patterns` / `--no-use-patterns` – enable/use pattern database (default: enabled).
- `--pattern-db` – path to pattern JSON file (default: `~/.openclaw/workspace/smart_merge_patterns.json`).
- `--min-similarity` – Jaccard similarity threshold for pattern matching (0.0–1.0, default: 0.6).
- `--no-confirm` – skip confirmation prompt before merging.
- `--mock-model` – simulate AI response (for testing without API key).

**First run example** (requires API key):

    export OPENROUTER_API_KEY="your-key"
    python3 smart_merge.py --files "contracts/*.pdf" --output final.pdf

The script will display extracted signatures, ask the model for order, show the proposed order, ask for confirmation, then merge and save the pattern.

Subsequent runs with similar documents will reuse the saved pattern.

---

### Delete Pages

    python3 delete_pages.py input.pdf --pages 2,4,6-9 --output cleaned.pdf

### Reorder Pages (Move)

    python3 sort_pages.py input.pdf --move 5:2,8:6 --output reordered.pdf

Moves page 5 to position 2, then page 8 to position 6 (after the first move).

### Edit Page Text

Requires the [nano-pdf](https://github.com/your-repo/nano-pdf) skill.

    python3 edit_page_text.py input.pdf --page 3 --instruction "Fix typo: 'teh' -> 'the'" --output edited.pdf

### Check Coherence

    python3 check_coherence.py input.pdf --threshold 0.3

Reports overlap scores between consecutive pages. Values below threshold indicate possible page breaks.

### Extract Text (with optional OCR)

    # Extract using PyPDF2 (for text‑based PDFs)
    python3 ocr_pages.py input.pdf --pages 1-3 --text-output text.txt

    # Force OCR for scanned pages (requires Tesseract)
    python3 ocr_pages.py input.pdf --pages 1-3 --ocr --text-output text.txt

### Extract Pages as Images

    python3 extract_images.py input.pdf --output-dir images/ --format png --dpi 200 --pages 1-5

### Add Watermark

    # Text watermark
    python3 add_watermark.py input.pdf --text "CONFIDENTIAL" --color "#FF0000" --opacity 0.4 --angle 30 --output watermarked.pdf

    # Image watermark (PNG with transparency recommended)
    python3 add_watermark.py input.pdf --image watermark.png --opacity 0.5 --output watermarked.pdf

### Rotate Pages

    python3 rotate_pages.py input.pdf --degrees 90 --pages 1-3 --output rotated.pdf
    # Omit --pages to rotate all pages

### Extract Metadata

    python3 extract_metadata.py input.pdf --output meta.json

### Make PDF Searchable (OCR Text Layer)

Uses [OCRmyPDF](https://ocrmypdf.readthedocs.io/). System dependencies: `ghostscript`, `tesseract`, `poppler-utils`.

    python3 make_searchable.py scanned.pdf --output searchable.pdf --lang rus+eng --deskew --clean

Extra arguments after `--` are passed directly to OCRmyPDF. Example:

    python3 make_searchable.py in.pdf --out search.pdf --lang eng -- --pdfa-image-compression jpeg

---

## Notes

- **Page numbering:** 1‑based for all scripts except `edit_page_text.py` (which internally uses 0‑based for nano‑pdf).
- **`merge_content.py`** patterns are matched case‑insensitively.
- **`smart_merge.py`** extracts signatures from the first page only (first ~300 words). It filters stopwords, ignores names/toponyms unless they are at the start of a sentence/heading, and preserves numbers that follow markers like `№`, `#`, or words "номер", "номера", "номером".
- **`check_coherence.py`** uses simple sentence boundary detection; adjust threshold as needed.
- **Watermark opacity** and rotation are supported for both text and images.
- All scripts accept `--output` (or `-o`) to specify the output file/directory.
- The skill is designed to work within the OpenClaw environment, but the scripts can be run independently as long as dependencies are satisfied.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'PyPDF2'` | Install PyPDF2: `uv pip install PyPDF2` |
| `nano-pdf: command not found` | Install the [nano-pdf](https://github.com/your-repo/nano-pdf) skill. |
| OCR fails (`pytesseract.pytesseract.TesseractNotFoundError`) | Install Tesseract system package and ensure it is in PATH. |
| `pdf2image` errors | Install poppler-utils: `sudo apt-get install poppler-utils` |
| `make_searchable.py` missing ghostscript | Install ghostscript: `sudo apt-get install ghostscript` |
| `requests` module missing for `smart_merge.py` | Install requests: `uv pip install requests` |
| Watermark type errors (Decimal to float) | Use the latest version of the script (issue fixed). |

---

## License

MIT
