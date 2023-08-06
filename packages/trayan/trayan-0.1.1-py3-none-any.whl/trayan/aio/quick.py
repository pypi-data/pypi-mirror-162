from typing import Optional, Iterable

from .translator import AsyncTranslator
from ..models.translator import Language


async def async_detect(
        text: str,
        hints: Optional[Iterable[str]] = None,
        proxies: Optional[Iterable[str]] = None,
        is_ssl: bool = True
):
    async with AsyncTranslator(proxies=proxies, is_ssl=is_ssl) as t:
        return await t.detect(text=text, hints=hints)


async def async_translate(
        text: str,
        source_language: str = Language.EN,
        target_language: str = Language.RU,
        proxies: Optional[Iterable[str]] = None,
        is_ssl: bool = True
) -> str:
    async with AsyncTranslator(proxies=proxies, is_ssl=is_ssl) as t:
        return await t.translate(text=text, source_language=source_language, target_language=target_language)
