import os
from random import choice
from typing import Optional, Iterable

import aiofiles
from aiohttp import ClientSession, TCPConnector, ClientResponse

from ..base import BaseTranslator
from ..models.errors import BadResponse, SidParseError
from ..models.request import RequestMethod
from ..models.translator import ApiMethod, Language
from ..utils import cached_property


class AsyncTranslator(BaseTranslator):
    async def detect(self, text: str, hints: Optional[Iterable[str]] = None) -> Language:
        resp = await self._api_req(
            RequestMethod.GET,
            ApiMethod.DETECT,
            params=dict(
                sid=await self.sid,
                srv='tr-text',
                text=text,
                options=1
            ) | (dict(hint=hints if isinstance(hints, str) else ','.join(hints)) if hints else {}),
            headers={
                'Host': 'translate.yandex.net',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Origin': 'https://translate.yandex.ru',
                'Referer': 'https://translate.yandex.ru/',
            }
        )
        if resp.status == 200:
            return (await resp.json(encoding='utf-8')).get('lang')
        raise BadResponse(resp.content)

    async def translate(
            self,
            text: str,
            source_language: str = Language.EN,
            target_language: str = Language.RU
    ) -> str:
        resp = await self._api_req(
            RequestMethod.POST,
            ApiMethod.TRANSLATE,
            params=dict(
                id=await self.id,
                srv='tr-text',
                lang=f'{source_language}-{target_language}',
                reason='type-end',
                format='text',
                ajax=1,
            ),
            data=dict(
                text=text,
                options=4
            ),
            headers={
                'Host': 'translate.yandex.net',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Origin': 'https://translate.yandex.ru',
                'Referer': 'https://translate.yandex.ru/',
            },
        )
        if resp.status == 200:
            return (await resp.json(encoding='utf-8')).get('text')[0]
        raise BadResponse(resp.content)

    async def __aenter__(self):
        await self.close()
        self.start()
        return self

    async def __aexit__(self, *err):
        await self.close()

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None

    @cached_property(ttl=60 * 60 * 24 * 4)
    async def sid(self) -> str:
        if not self._check_cache():
            sid = await self._gen_sid()
            try:
                await self._save_cache(sid)
            except PermissionError:
                ...
            return sid
        return await self._get_cache()

    @property
    async def id(self) -> str:
        return f'{await self.sid}{self.suffix}'

    async def _save_cache(self, data: str) -> None:
        async with aiofiles.open(self._CACHE_PATH, 'w', encoding='utf8') as f:
            os.utime(self._CACHE_PATH, None)
            await f.write(data)

    async def _get_cache(self) -> Optional[str]:
        async with aiofiles.open(self._CACHE_PATH, 'r', encoding='utf8') as f:
            return await f.read()

    def _init_session(self, is_ssl: bool = True) -> ClientSession:
        return ClientSession(connector=TCPConnector(ssl=is_ssl))

    async def _gen_sid(self) -> str:
        resp = await self._req(
            RequestMethod.GET,
            url=self.BASE_SITE_URL,
            headers={
                'Host': 'translate.yandex.ru',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
            }
        )
        if sid := self._sid_reg_exp.findall(await resp.text('utf-8')):
            return '.'.join(i[::-1] for i in sid[0].split('.'))
        raise SidParseError()

    async def _req(
            self,
            method: 'RequestMethod',
            *,
            url: Optional[str] = None,
            params: Optional[dict] = None,
            data: Optional[dict] = None,
            headers: Optional[dict] = None,
    ) -> ClientResponse:
        return await self._session.request(
            method,
            url or self.BASE_SITE_URL,
            params=params,
            data=data,
            headers={'User-Agent': self.USER_AGENT.random} | (headers or {}),
            proxy=self._get_proxy(),
        )

    async def _api_req(
            self,
            method: 'RequestMethod',
            api_method: 'ApiMethod',
            *,
            params: Optional[dict] = None,
            data: Optional[dict] = None,
            headers: Optional[dict] = None
    ) -> ClientResponse:
        return await self._req(
            method,
            url=f'{self.BASE_API_URL}{api_method}',
            params=params,
            data=data,
            headers=headers
        )

    def _get_proxy(self) -> Optional[str]:
        if self._proxies:
            return choice(self._proxies)
