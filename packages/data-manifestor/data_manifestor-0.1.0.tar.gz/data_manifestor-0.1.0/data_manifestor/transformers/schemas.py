from marshmallow import (
    Schema,
    ValidationError,
    fields,
    post_load,
    validate,
    validates_schema,
)

from .. import dataclasses


class Dataclass(Schema):

    __model__ = None

    @post_load
    def make_dataclass(self, data: dict, **kwargs):
        return self.__model__(**data)


class Template(Dataclass):

    __model__ = dataclasses.Template

    name = fields.String()
    path_prefix = fields.String(dump_default="{}-{}-{}")
    path_patterns = fields.List(fields.String())
