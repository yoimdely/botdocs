from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from .legal import DISCLAIMER_TEXT
from .templates_loader import TemplateLoader


class PdfBuilder:
    _font_registered = False

    def __init__(self, template_loader: TemplateLoader) -> None:
        self.template_loader = template_loader

    def _ensure_font(self) -> str:
        """Register bundled DejaVuSerif fonts to render Cyrillic correctly."""

        if PdfBuilder._font_registered:
            return "DejaVuSerif"

        fonts_dir = Path(__file__).resolve().parent.parent / "data" / "fonts"
        regular = fonts_dir / "DejaVuSerif.ttf"
        bold = fonts_dir / "DejaVuSerif-Bold.ttf"

        pdfmetrics.registerFont(TTFont("DejaVuSerif", str(regular)))
        pdfmetrics.registerFont(TTFont("DejaVuSerif-Bold", str(bold)))

        PdfBuilder._font_registered = True
        return "DejaVuSerif"

    def build(self, template_name: str, context: Dict[str, str]) -> BytesIO:
        font_name = self._ensure_font()
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            leftMargin=30 * mm,
            rightMargin=10 * mm,
        )
        story = []
        styles = getSampleStyleSheet()
        registered_fonts = set(pdfmetrics.getRegisteredFontNames())
        title_font = "DejaVuSerif-Bold" if "DejaVuSerif-Bold" in registered_fonts else font_name

        normal = styles["Normal"]
        normal.fontSize = 14
        normal.fontName = font_name
        normal.leading = 18
        normal.firstLineIndent = 12.5 * mm
        normal.alignment = TA_JUSTIFY
        normal.spaceAfter = 6

        title_style = ParagraphStyle(
            "GOSTTitle",
            parent=normal,
            fontSize=16,
            leading=20,
            firstLineIndent=0,
            fontName=title_font,
            alignment=TA_CENTER,
            spaceAfter=12,
        )

        meta_style = ParagraphStyle(
            "GOSTMeta",
            parent=normal,
            fontSize=12,
            leading=14,
            firstLineIndent=0,
            alignment=TA_RIGHT,
            spaceAfter=6,
        )

        footer_style = ParagraphStyle(
            "GOSTFooter",
            parent=normal,
            firstLineIndent=0,
            spaceBefore=6,
        )
        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=normal,
            fontSize=10,
            textColor="#555555",
            firstLineIndent=0,
            spaceBefore=12,
        )

        rendered = self.template_loader.render(template_name, context)

        first_content_added = False
        for line in rendered.split("\n"):
            if not line.strip():
                continue

            if not first_content_added:
                story.append(Paragraph(line, title_style))
                first_content_added = True
                continue

            if line.lower().startswith("г. "):
                story.append(Paragraph(line, meta_style))
                continue

            story.append(Paragraph(line, normal))
            story.append(Spacer(1, 8))

        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}", footer_style))
        story.append(Paragraph("Подпись стороны: _____________________", footer_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(DISCLAIMER_TEXT, disclaimer_style))
        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def ensure_template_directory(path: str) -> Path:
        directory = Path(path)
        directory.mkdir(parents=True, exist_ok=True)
        return directory
