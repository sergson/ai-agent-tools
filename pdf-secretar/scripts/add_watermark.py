#!/usr/bin/env python3
"""
Add text or image watermark to all pages of a PDF.
"""
import sys
import argparse
from pathlib import Path
from io import BytesIO

def add_workspace_to_path():
    ws = Path.home() / ".openclaw" / "workspace"
    venv = ws / ".venv" / "lib" / "python3.12" / "site-packages"
    if venv.exists():
        sys.path.insert(0, str(venv))

def ensure_deps():
    try:
        import PyPDF2  # noqa: F401
        from reportlab.pdfgen import canvas  # noqa: F401
        from reportlab.lib.colors import Color  # noqa: F401
        return True
    except ImportError:
        print("ERROR: Установите: uv pip install PyPDF2 reportlab", file=sys.stderr)
        return False

def parse_color(hexstr):
    """Convert #RRGGBB or tuple string to reportlab Color."""
    from reportlab.lib.colors import Color
    if hexstr.startswith('#'):
        r = int(hexstr[1:3], 16) / 255
        g = int(hexstr[3:5], 16) / 255
        b = int(hexstr[5:7], 16) / 255
        return Color(r, g, b)
    # fallback: named color? Not needed
    return Color(0.5, 0.5, 0.5)

def create_watermark_page(page_width, page_height, text=None, image_path=None, **kwargs):
    """
    Create a PDF page with watermark (text or image) using reportlab.
    Returns a PyPDF2 PageObject.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    packet = BytesIO()
    # Convert to float explicitly
    width = float(page_width)
    height = float(page_height)
    c = canvas.Canvas(packet)
    c.setPageSize((width, height))
    c.setFillAlpha(kwargs.get('opacity', 0.3))

    if image_path:
        from reportlab.lib.utils import ImageReader
        img = ImageReader(image_path)
        # Draw image centered (assuming image size)
        img_width, img_height = img.getSize()
        # Scale if needed
        max_size = min(width, height) * 0.5
        scale = min(1.0, max_size / max(img_width, img_height))
        draw_w = img_width * scale
        draw_h = img_height * scale
        x = (width - draw_w) / 2
        y = (height - draw_h) / 2
        c.drawImage(img, x, y, draw_w, draw_h, mask='auto')
    else:
        text = text or "CONFIDENTIAL"
        font_size = kwargs.get('font_size', 60)
        c.setFont("Helvetica", font_size)
        color = parse_color(kwargs.get('color', '#808080'))
        c.setFillColor(color)
        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(kwargs.get('angle', 45))
        c.drawCentredString(0, 0, text)
        c.restoreState()

    c.save()
    packet.seek(0)
    from PyPDF2 import PdfReader
    return PdfReader(packet).pages[0]

def add_watermark(input_pdf, output_pdf, text=None, image=None, **kwargs):
    from PyPDF2 import PdfReader, PdfWriter

    input_path = Path(input_pdf)
    f_in = open(input_path, 'rb')
    try:
        reader = PdfReader(f_in)
        writer = PdfWriter()

        for page in reader.pages:
            # Create watermark sized to this page
            wm_page = create_watermark_page(
                page.mediabox.width,
                page.mediabox.height,
                text=text,
                image_path=image,
                **kwargs
            )
            page.merge_page(wm_page)
            writer.add_page(page)

        with open(output_pdf, 'wb') as f_out:
            writer.write(f_out)
        print(f"Watermarked {len(reader.pages)} pages -> {output_pdf}")
    finally:
        f_in.close()

if __name__ == "__main__":
    add_workspace_to_path()
    if not ensure_deps():
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Add watermark to PDF")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("--output", "-o", default="watermarked.pdf", help="Output PDF file")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Watermark text")
    group.add_argument("--image", help="Watermark image file (PNG with transparency recommended)")
    parser.add_argument("--font-size", type=int, default=60, help="Font size for text watermark")
    parser.add_argument("--color", default="#808080", help="Text color in hex, e.g., #808080")
    parser.add_argument("--opacity", type=float, default=0.3, help="Opacity 0.0-1.0")
    parser.add_argument("--angle", type=float, default=45, help="Rotation angle in degrees")
    args = parser.parse_args()

    add_watermark(args.input_pdf, args.output,
                  text=args.text, image=args.image,
                  font_size=args.font_size, color=args.color,
                  opacity=args.opacity, angle=args.angle)
