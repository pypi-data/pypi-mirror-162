from typing import Optional, Iterable

from .translator import Translator
from ..models.translator import Language


def detect(
        text: str,
        hints: Optional[Iterable[str]] = None,
        proxies: Optional[Iterable[str]] = None,
        is_ssl: bool = True
) -> Language:
    with Translator(proxies=proxies, is_ssl=is_ssl) as t:
        return t.detect(text=text, hints=hints)


def translate(
        text: str,
        source_language: str = Language.EN,
        target_language: str = Language.RU,
        proxies: Optional[Iterable[str]] = None,
        is_ssl: bool = True
) -> str:
    with Translator(proxies=proxies, is_ssl=is_ssl) as t:
        return t.translate(text=text, source_language=source_language, target_language=target_language)
