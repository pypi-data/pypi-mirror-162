import os
import re
from base64 import b64decode
from random import randint
from time import time
from typing import Optional, Iterable, Dict

import pyuser_agent


class BaseTranslator:
    BASE_SITE_URL = b64decode(b'aHR0cHM6Ly90cmFuc2xhdGUueWFuZGV4LnJ1Lw==').decode('utf-8')
    BASE_API_URL = b64decode(b'aHR0cHM6Ly90cmFuc2xhdGUueWFuZGV4Lm5ldC9hcGkvdjEvdHIuanNvbi8=').decode('utf-8')
    SUPPORTED_LANGS = {
        'az': 'Azerbaijani',
        'ml': 'Malayalam',
        'sq': 'Albanian',
        'mt': 'Maltese',
        'am': 'Amharic',
        'mk': 'Macedonian',
        'en': 'English',
        'mi': 'Maori',
        'ar': 'Arabic',
        'mr': 'Marathi',
        'hy': 'Armenian',
        'mhr': 'Mari',
        'af': 'Afrikaans',
        'mn': 'Mongolian',
        'eu': 'Basque',
        'de': 'German',
        'ba': 'Bashkir',
        'ne': 'Nepalese',
        'be': 'Belarusian',
        'no': 'Norwegian',
        'bn': 'Bengal',
        'pa': 'Punjabi',
        'my': 'Burmese',
        'pap': 'Papiamento',
        'bg': 'Bulgarian',
        'fa': 'Persian',
        'bs': 'Bosnian',
        'pl': 'Polish',
        'cy': 'Welsh',
        'pt': 'Portuguese',
        'hu': 'Hungarian',
        'ro': 'Romanian',
        'vi': 'Vietnamese',
        'ru': 'Russian',
        'ht': 'Haitian (Creole)',
        'ceb': 'Cebuano',
        'gl': 'Galician',
        'sr': 'Serbian',
        'nl': 'Dutch',
        'si': 'Sinhalese',
        'mrj': 'Hill Mari',
        'sk': 'Slovak',
        'el': 'Greek',
        'sl': 'Slovenian',
        'ka': 'Georgian',
        'sw': 'Swahili',
        'gu': 'Gujarati',
        'su': 'Sundanese',
        'da': 'Danish',
        'tg': 'Tajik',
        'he': 'Hebrew',
        'th': 'Thai',
        'yi': 'Yiddish',
        'tl': 'Tagalog',
        'id': 'Indonesian',
        'ta': 'Tamil',
        'ga': 'Irish',
        'tt': 'Tartar',
        'it': 'Italian',
        'te': 'Telugu',
        'is': 'Icelandic',
        'tr': 'Turkish',
        'es': 'Spanish',
        'udm': 'Udmurt',
        'kk': 'Kazakh',
        'uz': 'Uzbek',
        'kn': 'Kannada',
        'uk': 'Ukrainian',
        'ca': 'Catalan',
        'ur': 'Urdu',
        'ky': 'Kirghiz',
        'fi': 'Finnish',
        'zh': 'Chinese',
        'fr': 'French',
        'ko': 'Korean',
        'hi': 'Hindi',
        'xh': 'Xhosa',
        'hr': 'Croatian',
        'km': 'Khmer',
        'cs': 'Czech',
        'lo': 'Laotian',
        'sv': 'Swedish',
        'la': 'Latin',
        'gd': 'Scottish',
        'lv': 'Latvian',
        'et': 'Estonian',
        'lt': 'Lithuanian',
        'eo': 'Esperanto',
        'lb': 'Luxembourg',
        'jv': 'Javanese',
        'mg': 'Malagasy',
        'ja': 'Japanese',
        'ms': 'Malay'
    }

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

    @classmethod
    @property
    def supported_langs(cls) -> Dict[str, str]:
        return cls.SUPPORTED_LANGS

    @classmethod
    def get_supported_langs(cls) -> Dict[str, str]:
        return cls.supported_langs

    def _check_cache(self) -> bool:
        if os.path.exists(self._CACHE_PATH):
            try:
                return os.path.isfile(self._CACHE_PATH) & \
                       ((time() - os.path.getmtime(self._CACHE_PATH)) < 60 * 60 * 24 * 4)
            except PermissionError:
                ...
