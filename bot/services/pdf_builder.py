from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple

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
        """Register a Cyrillic-capable font once using system fonts only.

        We avoid bundling TTF/OTF files; instead, we look up common free fonts
        that ship with most Linux/Windows/macOS systems (DejaVu/Liberation/Noto/Arial)
        and embed the first one we find.
        """

        def iter_candidates() -> Sequence[Tuple[str, Path, Optional[Path]]]:
            return (
                (
                    "DejaVuSerif",
                    Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
                    Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
                ),
                (
                    "DejaVuSans",
                    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
                    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
                ),
                (
                    "LiberationSerif",
                    Path("/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf"),
                    Path("/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf"),
                ),
                (
                    "NotoSans",
                    Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
                    Path("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"),
                ),
                (
                    "Arial",
                    Path("C:/Windows/Fonts/arial.ttf"),
                    Path("C:/Windows/Fonts/arialbd.ttf"),
                ),
                (
                    "ArialMac",
                    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
                    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
                ),
            )

        if PdfBuilder._font_registered:
            return "CLEAN_DOC_FONT"

        for _family, regular, bold in iter_candidates():
            if not regular.exists():
                continue

            pdfmetrics.registerFont(TTFont("CLEAN_DOC_FONT", str(regular)))
            if bold and bold.exists():
                pdfmetrics.registerFont(TTFont("CLEAN_DOC_FONT_BOLD", str(bold)))
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
            leftMargin=30 * mm,
            rightMargin=10 * mm,
        )
        story = []
        styles = getSampleStyleSheet()
        registered_fonts = set(pdfmetrics.getRegisteredFontNames())
        title_font = "CLEAN_DOC_FONT_BOLD" if "CLEAN_DOC_FONT_BOLD" in registered_fonts else font_name

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
