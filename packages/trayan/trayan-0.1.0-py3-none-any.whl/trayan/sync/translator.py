import os
from random import choice
from typing import Optional, Iterable

from requests import Session, Response

from trayan.base import BaseTranslator
from trayan.models.errors import SidParseError, BadResponse
from trayan.models.request import RequestMethod
from trayan.models.translator import Language, ApiMethod
from trayan.utils import cached_property


class Translator(BaseTranslator):
    def detect(self, text: str, hints: Optional[Iterable[str]] = None) -> Language:
        resp = self._api_req(
            RequestMethod.GET,
            ApiMethod.DETECT,
            params=dict(
                sid=self.sid,
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
        if resp.status_code == 200:
            return resp.json().get('lang')
        raise BadResponse(resp.content)

    def translate(
            self,
            text: str,
            source_language: str = Language.EN,
            target_language: str = Language.RU
    ) -> str:
        resp = self._api_req(
            RequestMethod.POST,
            ApiMethod.TRANSLATE,
            params=dict(
                id=self.id,
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
        if resp.status_code == 200:
            return resp.json().get('text')[0]
        raise BadResponse(resp.content)

    def __enter__(self):
        self.close()
        self.start()
        return self

    def __exit__(self, *err):
        self.close()

    def close(self) -> None:
        if self._session:
            self._session.close()
        self._session = None

    @cached_property(ttl=60 * 60 * 24 * 4)
    def sid(self) -> str:
        if not self._check_cache():
            sid = self._gen_sid()
            try:
                self._save_cache(sid)
            except PermissionError:
                ...
            return sid
        try:
            return self._get_cache()
        except PermissionError:
            return self._gen_sid()

    @property
    def id(self) -> str:
        return f'{self.sid}{self.suffix}'

    def _save_cache(self, data: str) -> None:
        with open(self._CACHE_PATH, 'w', encoding='utf8') as f:
            os.utime(self._CACHE_PATH, None)
            f.write(data)

    def _get_cache(self) -> Optional[str]:
        with open(self._CACHE_PATH, 'r', encoding='utf8') as f:
            return f.read()

    def _init_session(self, is_ssl: bool = True) -> Session:
        session = Session()

        session.verify = is_ssl
        session.trust_env = is_ssl

        return session

    def _gen_sid(self) -> str:
        resp = self._req(
            RequestMethod.GET,
            url=self.BASE_SITE_URL,
            headers={
                'Host': 'translate.yandex.ru',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
            }
        )
        if sid := self._sid_reg_exp.findall(resp.content.decode('utf-8')):
            return '.'.join(i[::-1] for i in sid[0].split('.'))
        raise SidParseError()

    def _req(
            self,
            method: 'RequestMethod',
            *,
            url: Optional[str] = None,
            params: Optional[dict] = None,
            data: Optional[dict] = None,
            headers: Optional[dict] = None,
    ) -> Response:
        return self._session.request(
            method,
            url or self.BASE_SITE_URL,
            params=params,
            data=data,
            headers={'User-Agent': self.USER_AGENT.random} | (headers or {}),
            proxies=self._get_proxies(),
        )

    def _api_req(
            self,
            method: 'RequestMethod',
            api_method: 'ApiMethod',
            *,
            params: Optional[dict] = None,
            data: Optional[dict] = None,
            headers: Optional[dict] = None
    ) -> Response:
        return self._req(
            method,
            url=f'{self.BASE_API_URL}{api_method}',
            params=params,
            data=data,
            headers=headers
        )

    def _get_proxies(self) -> Optional[dict]:
        if self._proxies:
            proxy = choice(self._proxies)
            return {
                'http': proxy,
                'https': proxy
            }
