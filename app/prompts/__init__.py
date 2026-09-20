"""
Prompt engineering templates package.
"""

from app.prompts.email import build_email_prompt
from app.prompts.report import build_report_prompt
from app.prompts.technical import build_technical_prompt
from app.prompts.general import build_general_prompt

__all__ = [
    "build_email_prompt",
    "build_report_prompt",
    "build_technical_prompt",
    "build_general_prompt",
]
