---
name: pdf-secretar
description: "Advanced PDF manipulation: split by page ranges or list, merge in various orders (filename, date, content-based), sort pages, delete pages, edit text via nano-pdf, check text coherence between pages, OCR pages with text extraction, extract pages as images, add watermark, rotate pages, extract metadata, make searchable PDF. Use for complex document processing tasks beyond simple splitting."
---

# PDF Secretary Skill

Comprehensive toolkit for advanced PDF operations. Handles splitting, merging, sorting, deleting, editing, coherence checking, OCR, image extraction, watermarking, rotation, metadata extraction, and creating searchable PDFs.

## Quick Start

### Split PDF by ranges
```bash
python3 scripts/split_pages.py input.pdf --ranges 1-3,5,7-9 --output-dir pages/
```

### Merge PDFs by name order
```bash
python3 scripts/merge_pages.py "pages/*.pdf" --order name --output merged.pdf
```

### Merge PDFs by content patterns
```bash
python3 scripts/merge_content.py "docs/*.pdf" --patterns "договор,акт,счёт" --output merged.pdf
```

### Delete pages
```bash
python3 scripts/delete_pages.py input.pdf --pages 2,4,6-9 --output cleaned.pdf
```

### Move pages (reorder)
```bash
python3 scripts/sort_pages.py input.pdf --move 5:2,8:6 --output reordered.pdf
```

### Edit page text via nano-pdf
```bash
python3 scripts/edit_page_text.py input.pdf --page 3 --instruction "Fix typo: 'teh' -> 'the'" --output edited.pdf
```

### Check coherence between pages
```bash
python3 scripts/check_coherence.py input.pdf --threshold 0.3
```

### Extract text (with optional OCR)
```bash
python3 scripts/ocr_pages.py input.pdf --pages 1-3 --text-output text.txt
# For scanned PDFs add --ocr (requires tesseract, pdf2image)
```

### Extract pages as images
```bash
python3 scripts/extract_images.py input.pdf --output-dir images/ --format png --dpi 200 --pages 1-5
```

### Add watermark (text or image)
```bash
python3 scripts/add_watermark.py input.pdf --text "CONFIDENTIAL" --color "#FF0000" --opacity 0.4 --angle 30 --output watermarked.pdf
# Or with image:
python3 scripts/add_watermark.py input.pdf --image watermark.png --output watermarked.pdf
```

### Rotate pages
```bash
python3 scripts/rotate_pages.py input.pdf --degrees 90 --pages 1-3 --output rotated.pdf
# Rotate all pages if --pages omitted
```

### Extract metadata
```bash
python3 scripts/extract_metadata.py input.pdf --output meta.json
```

### Make PDF searchable (OCR text layer)
```bash
python3 scripts/make_searchable.py scanned.pdf --output searchable.pdf --lang rus+eng --deskew --clean
```

### Intelligent merge (content-based ordering)
```bash
python3 scripts/smart_merge.py "docs/*.pdf" --output merged.pdf
# First run: asks OpenRouter model for order (requires OPENROUTER_API_KEY). After confirmation saves template.
# Templates stored by default at /media/temp/.smart_merge/patterns.json (customizable via --pattern-db).
# Use explicit order: --order "договор,техническое_задание,календарный_план,смета,акт,заявление"
# Skip confirmation: --no-confirm
# Disable patterns: --use-patterns false
# Note: Input files and output must reside under /media/temp (security restriction).
```

## What This Skill Does

| Function | Script | Description |
|----------|--------|-------------|
| Разбивка | `split_pages.py` | Разбивает PDF по диапазонам или списку страниц |
| Объединение (имя/дата/список) | `merge_pages.py` | Объединяет PDF по порядку имени, даты создания или из списка |
| Объединение (по содержимому) | `merge_content.py` | Сортирует файлы по поиску шаблонов в тексте, затем объединяет |
| Удаление страниц | `delete_pages.py` | Удаляет указанные страницы |
| Перестановка | `sort_pages.py` | Перемещает страницы (FROM:TO) внутри документа |
| Правка текста | `edit_page_text.py` | Правка текста на конкретной странице через nano-pdf |
| Проверка связности | `check_coherence.py` | Анализирует перекрытие предложений между соседними страницами |
| OCR / извлечение текста | `ocr_pages.py` | Извлекает текст (PyPDF2 или через OCR) в .txt |
| Изображения | `extract_images.py` | Конвертирует страницы в PNG/JPEG с заданным DPI |
| Водяной знак | `add_watermark.py` | Накладывает текстовый или графический водяной знак |
| Поворот | `rotate_pages.py` | Поворачивает страницы на 90/180/270 градусов |
| Метаданные | `extract_metadata.py` | Извлекает метаданные PDF (title, author, dates, etc.) |
| Поисковый PDF (Searchable) | `make_searchable.py` | Добавляет текстовый слой OCR к сканированному PDF (требует ghostscript, tesseract, poppler) |
| Интеллектуальное объединение | `smart_merge.py` | Объединяет PDF в логическом порядке на основе сигнатур содержимого, с обучением шаблонов и подтверждением. Может использовать OpenRouter для определения порядка при первом запуске. |

## Requirements

### Core (обязательно)
- Python 3.8+
- PyPDF2: `uv pip install PyPDF2`

### Optional dependencies
- **OCR (скан документы)**: `uv pip install pytesseract pdf2image pillow`
  + System: `tesseract-ocr`, `poppler-utils`
- **Watermark (текстовый)**: `uv pip install reportlab`
- **Image extraction**: `uv pip install pdf2image pillow`
  + System: `poppler-utils` (для `pdftoppm`)
- **Make searchable PDF**: `uv pip install ocrmypdf`
  + System: `ghostscript`, `tesseract-ocr`, `poppler-utils`

### System packages (Ubuntu/Debian)
```bash
sudo apt-get install poppler-utils tesseract-ocr ghostscript
```

## Installation

Скилл упаковывается в `pdf-secretar.skill` и устанавливается в `~/.npm-global/lib/node_modules/openclaw/skills/` распаковкой.

## Notes

- Номера страниц: 1-индексация (первая страница = 1), кроме `nano-pdf` (где 0-индексация)
- В `merge_content.py` шаблоны ищутся case-insensitively. Файлы, где найден более ранний шаблон, идут первыми.
- `check_coherence.py` использует простой графемный анализ; порог 0.0-1.0 (ниже = подозрительный разрыв).
- `add_watermark.py` для градиентов/изображений требует `reportlab`.
- Все скрипты принимают `--output` для указания выходного файла; по умолчанию `output.pdf` в текущей директории.
- `make_searchable.py` использует `ocrmypdf` для создания текстового слоя. Убедитесь, что ghostscript установлен в системе.
- `smart_merge.py`:
  - Шаблоны хранятся в `/media/temp/.smart_merge/patterns.json` (можно изменить через `--pattern-db`).
  - Входные файлы и выходной путь должны находиться внутри `/media/temp` (безопасность).
  - Для LLM-запроса используется OpenRouter; модель может быть изменена в коде (по умолчанию `arcee-ai/trinity-large-preview:free`).

## Troubleshooting

- **ModuleNotFoundError**: убедитесь, что PyPDF2 установлен в workspace `.venv`.
- **nano-pdf not found**: установите скилл `nano-pdf`.
- **OCR errors**: проверьте `tesseract` и `pdftoppm` в системе.
- **Watermark type error**: преобразование Decimal → float исправлено; используйте последнюю версию скрипта.
- **make_searchable missing ghostscript**: установите `sudo apt-get install ghostscript`.
