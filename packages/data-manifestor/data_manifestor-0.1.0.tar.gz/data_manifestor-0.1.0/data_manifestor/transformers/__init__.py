from ..dataclasses import Template
from .schemas import Template as TemplateSchema

template_schema = TemplateSchema()


def dict_to_template(data: dict) -> Template:
    return template_schema.load(data)
