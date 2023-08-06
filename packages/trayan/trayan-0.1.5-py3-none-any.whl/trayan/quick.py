from typing import Dict

from .base import BaseTranslator


def get_supported_langs() -> Dict[str, str]:
    return BaseTranslator.get_supported_langs()
