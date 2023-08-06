import os
import re
from random import randint
from time import time
from typing import Optional, Iterable

import pyuser_agent


class BaseTranslator:
    BASE_SITE_URL = 'https://translate.yandex.ru/'
    BASE_API_URL = 'https://translate.yandex.net/api/v1/tr.json/'

    USER_AGENT = pyuser_agent.UA()

    _SID_REG_EXP = r'SID\s?:\s?[\'"]([^\'"]+)[\'"]'

    _CACHE_PATH = os.path.join(os.path.expanduser('~'), '.trayan.key')

    def __init__(
            self,
            proxies: Optional[Iterable[str]] = None,
            is_ssl: bool = True
    ):
        self._session = None

        self._proxies = (proxies,) if isinstance(proxies, str) else proxies or ()
        self._is_ssl = is_ssl

        self._sid_reg_exp = re.compile(self._SID_REG_EXP)

        self.start()

    def start(self) -> None:
        self._session = self._init_session(self._is_ssl)

    @property
    def suffix(self) -> str:
        return f'-{randint(0, 9)}-0'

    def _check_cache(self) -> bool:
        return os.path.exists(self._CACHE_PATH) & \
               os.path.isfile(self._CACHE_PATH) & \
               ((time() - os.path.getmtime(self._CACHE_PATH)) < 60 * 60 * 24 * 4)
