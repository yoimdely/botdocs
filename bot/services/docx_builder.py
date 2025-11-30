from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Dict

from docx import Document
from docx.shared import Pt

from .legal import DISCLAIMER_TEXT
from .templates_loader import TemplateLoader


class DocxBuilder:
    def __init__(self, template_loader: TemplateLoader) -> None:
        self.template_loader = template_loader

    def build(self, template_name: str, context: Dict[str, str]) -> bytes:
        document = Document()
        rendered = self.template_loader.render(template_name, context)

        for line in rendered.split("\n"):
            if line.strip():
                document.add_paragraph(line)
            else:
                document.add_paragraph("")

        document.add_paragraph("")
        document.add_paragraph(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        document.add_paragraph("Подпись стороны: _____________________")
        document.add_paragraph("")
        disclaimer_paragraph = document.add_paragraph(DISCLAIMER_TEXT)
        disclaimer_paragraph.runs[0].font.size = Pt(8)

        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()
