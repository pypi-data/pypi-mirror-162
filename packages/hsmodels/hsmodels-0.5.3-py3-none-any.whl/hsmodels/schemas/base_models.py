from datetime import datetime
from typing import Any, Callable, Dict, Optional, Union

from pydantic import BaseModel


class BaseMetadata(BaseModel):
    def dict(
        self,
        *,
        include: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        exclude: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = True,
        to_rdf: bool = False,
    ) -> 'DictStrAny':
        """
        Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.

        Checks the config for a schema_config dictionary_field and converts a dictionary to a list of key/value pairs.
        This converts the dictionary to a format that can be described in a json schema (which can be found below in the
        schema_extra staticmethod.

        Override the default of exclude_none to True
        """
        d = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

        if to_rdf and hasattr(self.Config, "schema_config"):
            schema_config = self.Config.schema_config
            if "dictionary_field" in schema_config:
                for field in schema_config["dictionary_field"]:
                    field_value = d[field]
                    d[field] = [{"key": key, "value": value} for key, value in field_value.items()]
        return d

    def json(
        self,
        *,
        include: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        exclude: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = True,
        encoder: Optional[Callable[[Any], Any]] = None,
        **dumps_kwargs: Any,
    ) -> str:
        """
        Generate a JSON representation of the model, `include` and `exclude` arguments as per `dict()`.

        `encoder` is an optional function to supply as `default` to json.dumps(), other arguments as per `json.dumps()`.

        Override the default of exclude_none to True
        """
        return super().json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            **dumps_kwargs,
        )

    class Config:
        validate_assignment = True

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model) -> None:
            if hasattr(model.Config, "schema_config"):
                schema_config = model.Config.schema_config
                if "read_only" in schema_config:
                    # set readOnly in json schema
                    for field in schema_config["read_only"]:
                        if field in schema['properties']:  # ignore unknown properties for inheritance
                            schema['properties'][field]['readOnly'] = True
                if "dictionary_field" in schema_config:
                    for field in schema_config["dictionary_field"]:
                        if field in schema['properties']:  # ignore unknown properties for inheritance
                            prop = schema["properties"][field]
                            prop.pop('default', None)
                            prop.pop('additionalProperties', None)
                            prop['type'] = "array"
                            prop['items'] = {
                                "type": "object",
                                "title": "Key-Value",
                                "description": "A key-value pair",
                                "default": [],
                                "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
                            }


class BaseCoverage(BaseMetadata):
    def __str__(self):
        return "; ".join(
            [
                "=".join([key, val.isoformat() if isinstance(val, datetime) else str(val)])
                for key, val in self.__dict__.items()
                if key != "type" and val
            ]
        )
