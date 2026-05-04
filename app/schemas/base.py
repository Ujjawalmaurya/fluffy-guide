"""
SkillBridge AI — Base Schema
Common Pydantic configuration for all models.
"""
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Base schema for all SkillBridge AI models.
    Enforces strict whitespace stripping and enum value usage.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
        populate_by_name=True
    )
