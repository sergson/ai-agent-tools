---
name: pdf-secretar
description: "Advanced PDF manipulation: split by page ranges or list, merge in various orders (filename, date, content-based), sort pages, delete pages, edit text via nano-pdf, check text coherence between pages, OCR pages with text extraction, extract pages as images, add watermark, rotate pages, extract metadata, make searchable PDF. Use for complex document processing tasks beyond simple splitting."
---

# PDF Secretary Skill

Comprehensive toolkit for advanced PDF operations. Handles splitting, merging, sorting, deleting, editing, coherence checking, OCR, image extraction, watermarking, rotation, metadata extraction, and creating searchable PDFs.

## Simplified Launch (for Agents)

Instead of calling individual scripts with full paths, you can use a single command:

```bash
pdf-secretar <command> [arguments...]
```

Examples:
pdf-secretar merge_pages --input "*.pdf" --output result.pdf
pdf-secretar smart_merge --files "/media/temp/*.pdf" --no-confirm
pdf-secretar split_pages --input doc.pdf --pages 1-3,5

## Installation

The skill is packaged in `pdf-secretar.skill` and installed in `~/.openclaw/skills/` by unpacking.
After installing the skill, the launcher script is located at: ~/.openclaw/skills/pdf-secretar/bin/pdf-secretar
To use it from any directory, create a symbolic link in `~/.local/bin/` (make sure this directory exists and is in your `PATH`):
```bash
mkdir -p ~/.local/bin
ln -s ~/.openclaw/skills/pdf-secretar/bin/pdf-secretar ~/.local/bin/
```
If ~/.local/bin is not yet in your PATH, add the following line to your ~/.bashrc or ~/.profile: export PATH="$HOME/.local/bin:$PATH"
Then reload the configuration: source ~/.bashrc
Now you can run pdf-secretar from anywhere. To verify, type: pdf-secretar
You should see a list of available commands.

The command automatically uses Python from the virtual environment, so manual activation is not required.

The list of available commands matches the script names (without the .py extension).


## Quick Start

### Split PDF by ranges
```bash
pdf-secretar split_pages input.pdf --ranges 1-3,5,7-9 --output-dir pages/
```

### Merge PDFs by name order
```bash
pdf-secretar  merge_pages "pages/*.pdf" --order name --output merged.pdf
```

### Merge PDFs by content patterns
```bash
pdf-secretar  merge_content "docs/*.pdf" --patterns "договор,акт,счёт" --output merged.pdf
```

### Delete pages
```bash
pdf-secretar  delete_pages input.pdf --pages 2,4,6-9 --output cleaned.pdf
```

### Move pages (reorder)
```bash
pdf-secretar sort_pages input.pdf --move 5:2,8:6 --output reordered.pdf
```

### Edit page text via nano-pdf
```bash
pdf-secretar edit_page_text input.pdf --page 3 --instruction "Fix typo: 'teh' -> 'the'" --output edited.pdf
```

### Check coherence between pages
```bash
pdf-secretar check_coherence input.pdf --threshold 0.3
```

### Extract text (with optional OCR)
```bash
pdf-secretar ocr_pages input.pdf --pages 1-3 --text-output text.txt
# For scanned PDFs add --ocr (requires tesseract, pdf2image)
```

### Extract pages as images
```bash
pdf-secretar  extract_images input.pdf --output-dir images/ --format png --dpi 200 --pages 1-5
```

### Add watermark (text or image)
```bash
pdf-secretar add_watermark input.pdf --text "CONFIDENTIAL" --color "#FF0000" --opacity 0.4 --angle 30 --output watermarked.pdf
# Or with image:
pdf-secretar add_watermark input.pdf --image watermark.png --output watermarked.pdf
```

### Rotate pages
```bash
pdf-secretar  rotate_pages input.pdf --degrees 90 --pages 1-3 --output rotated.pdf
# Rotate all pages if --pages omitted
```

### Extract metadata
```bash
pdf-secretar  extract_metadata input.pdf --output meta.json
```

### Make PDF searchable (OCR text layer)
```bash
pdf-secretar  make_searchable scanned.pdf --output searchable.pdf --lang rus+eng --deskew --clean
```

### Intelligent merge (content-based ordering)
```bash
pdf-secretar smart_merge "docs/*.pdf" --output merged.pdf
# First run: asks OpenRouter model for order (requires OPENROUTER_API_KEY). After confirmation saves template.
# Templates stored by default at /media/temp/.smart_merge/patterns.json (customizable via --pattern-db).
# Use explicit order: --order "contract, technical specifications, schedule, estimate, act, application"
# Skip confirmation: --no-confirm
# Disable patterns: --use-patterns false
# Note: Input files and output must reside under /media/temp (security restriction).
```


## What This Skill Does

| Function | Script | Description |
|----------|-------------|
| Split | `split_pages.py` | Splits a PDF by page range or list |
| Merge (name/date/list) | `merge_pages.py` | Merge PDFs by name, creation date, or list |
| Merge (content) | `merge_content.py` | Sorts files by finding patterns in the text, then merges |
| Delete Pages | `delete_pages.py` | Deletes specified pages |
| Rearrange | `sort_pages.py` | Moves pages (FROM:TO) within the document |
| Edit Text | `edit_page_text.py` | Edit text on a specific page with nano-pdf |
| Coherence check | `check_coherence.py` | Analyzes sentence overlap between adjacent pages |
| OCR / Text Extraction | `ocr_pages.py` | Extracts text (PyPDF2 or via OCR) to .txt |
| Images | `extract_images.py` | Converts pages to PNG/JPEG with a specified DPI |
| Watermark | `add_watermark.py` | Adds a text or image watermark |
| Rotate | `rotate_pages.py` | Rotates pages 90/180/270 degrees |
| Metadata | `extract_metadata.py` | Extracts PDF metadata (title, author, dates, etc.) |
| Searchable PDF | `make_searchable.py` | Adds an OCR text layer to a scanned PDF (requires ghostscript, tesseract, poppler) |
| Smart Merging | `smart_merge.py` | Merges PDFs in a logical order based on content signatures, with template learning and validation. Can use OpenRouter to determine order on first run. |

## Requirements

### Core (required)
- Python 3.8+
- PyPDF2: `uv pip install PyPDF2`

### Optional dependencies
- **OCR (scanned documents)**: `uv pip install pytesseract pdf2image pillow` 
+ System: `tesseract-ocr`, `poppler-utils`
- **Watermark (text)**: `uv pip install reportlab`
- **Image extraction**: `uv pip install pdf2image pillow` 
+ System: `poppler-utils` (for `pdftoppm`)
- **Make searchable PDF**: `uv pip install ocrmypdf` 
+ System: `ghostscript`, `tesseract-ocr`, `poppler-utils`

### System packages (Ubuntu/Debian)
```bash
sudo apt-get install poppler-utils tesseract-ocr ghostscript
```


## Notes

- Page numbers: 1-indexed (first page = 1), except for `nano-pdf` (where 0-indexed)
- In `merge_content.py`, patterns are searched case-insensitively. Files that contain an earlier pattern are listed first.
- `check_coherence.py` uses simple grapheme analysis; the threshold is 0.0-1.0 (lower = suspicious discontinuity).
- `add_watermark.py` requires `reportlab` for gradients/images.
- All scripts accept `--output` to specify the output file; by default, `output.pdf` in the current directory.
- `make_searchable.py` uses `ocrmypdf` to create the text layer. Make sure ghostscript is installed on your system.
- `smart_merge.py`:
- Patterns are stored in `/media/temp/.smart_merge/patterns.json` (can be changed via `--pattern-db`).
- Input files and output path must be located in `/media/temp` (security).
- OpenRouter is used for LLM query; the model can be changed in code (default is `arcee-ai/trinity-large-preview:free`).

## Troubleshooting

- **ModuleNotFoundError**: Make sure PyPDF2 is installed in the `.venv` workspace.
- **nano-pdf not found**: Install the `nano-pdf` skill. 
- **OCR errors**: Check `tesseract` and `pdftoppm` on the system.
- **Watermark type error**: Decimal to float conversion fixed; use the latest version of the script.
- **make_searchable missing ghostscript**: Install `sudo apt-get install ghostscript`.