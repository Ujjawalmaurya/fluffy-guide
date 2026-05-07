"""
SkillBridge AI — Base Schema
Common Pydantic configuration for all models.
"""
from pydantic import BaseModel, ConfigDict, model_validator
from typing import Any


class BaseSchema(BaseModel):
    """
    Base schema for all SkillBridge AI models.
    Enforces strict whitespace stripping, enum value usage, and ORM compatibility.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True,
        from_attributes=True
    )

    @classmethod
    def get_config(cls, **kwargs) -> ConfigDict:
        """Helper to extend base config without losing settings."""
        config = dict(cls.model_config)
        config.update(kwargs)
        return ConfigDict(**config)

    @model_validator(mode="before")
    @classmethod
    def empty_strings_to_none(cls, data: Any) -> Any:
        """Globally convert empty strings or whitespace-only strings to None."""
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, str) and not v.strip():
                    data[k] = None
        return data
