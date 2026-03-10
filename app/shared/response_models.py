"""
Standard API response envelope. Every route returns this shape.
Keeps frontend parsing predictable.
"""
from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    error_code: str | None = None
    message: str | None = None


def ok(data: Any = None, message: str | None = None) -> dict:
    """Success response."""
    return {"success": True, "data": data, "message": message}


def err(error_code: str, message: str, details: dict = None) -> dict:
    """Error response — prefer raising AppError subclasses instead."""
    return {"success": False, "error_code": error_code, "message": message, "details": details or {}}
