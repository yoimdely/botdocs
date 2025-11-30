from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateLoader:
    def __init__(self, template_dir: Path) -> None:
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(searchpath=str(template_dir)),
            autoescape=select_autoescape(disabled_extensions=("jinja",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        template = self.env.get_template(template_name)
        return template.render(**context)
