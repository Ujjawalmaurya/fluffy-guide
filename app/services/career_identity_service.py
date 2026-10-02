"""
career_identity_service.py — Backwards-compatible export from app.modules.recommendations.
"""
from app.modules.recommendations.career_identity import (
    CareerIdentityService,
    career_identity_service,
)

__all__ = ["CareerIdentityService", "career_identity_service"]
