from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional

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
        """
        Register a Cyrillic-capable font once. We try common system fonts so PDF text renders properly.
        """
        if PdfBuilder._font_registered:
            return "CLEAN_DOC_FONT"

        font_paths = [
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows default
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux DejaVu
            "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS Arial
        ]
        font_path: Optional[str] = next((path for path in font_paths if Path(path).exists()), None)
        if font_path:
            pdfmetrics.registerFont(TTFont("CLEAN_DOC_FONT", font_path))
            PdfBuilder._font_registered = True
            return "CLEAN_DOC_FONT"

        # Fallback to Helvetica (may not render Cyrillic perfectly but keeps PDF generation working)
        return "Helvetica"

    def build(self, template_name: str, context: Dict[str, str]) -> BytesIO:
        font_name = self._ensure_font()
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
        )
        story = []
        styles = getSampleStyleSheet()
        normal = styles["Normal"]
        normal.fontSize = 11
        normal.fontName = font_name
        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=normal,
            fontSize=8,
            textColor="#555555",
        )

        rendered = self.template_loader.render(template_name, context)

        for line in rendered.split("\n"):
            if line.strip():
                story.append(Paragraph(line, normal))
                story.append(Spacer(1, 8))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal))
        story.append(Paragraph("Подпись стороны: _____________________", normal))
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
