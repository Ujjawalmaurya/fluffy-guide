"""
suggester package exports.
"""
from app.modules.resume_analysis.suggester.bullet_enhancer import (
    improve_bullet,
    batch_improve_bullets,
)
from app.modules.resume_analysis.suggester.summary_generator import generate_summary
from app.modules.resume_analysis.suggester.service import generate_suggestions

__all__ = [
    "improve_bullet",
    "batch_improve_bullets",
    "generate_summary",
    "generate_suggestions",
]
