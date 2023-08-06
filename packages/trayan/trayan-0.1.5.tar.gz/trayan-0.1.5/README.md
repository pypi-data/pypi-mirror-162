# trayan
awesome free asynchronous translator for python

## Installation
`pip install -U trayan`

## Usage
```python
async def use():
    from trayan import (
        Translator, AsyncTranslator,
        detect, translate,
        async_detect, async_translate,
        get_supported_langs
    )
    from trayan.models.translator import Language

    proxy = None  # 'scheme://ip:port'
    ru = 'красивый мужчина в отличных трусах'
    en = 'a handsome man in great underpants'

    with Translator(proxies=proxy, is_ssl=True) as t:
        print(f'{ru} — {t.detect(ru, Language.RU)}')
        print(f'ru-en — {t.translate(ru, Language.RU, Language.EN)}')

    print(f'{en} — {detect(en)}')
    print(f'en-ru — {translate(en)}')

    async with AsyncTranslator(proxies=(proxy,) if proxy else None, is_ssl=False) as t:
        print(f'{en} — {await t.detect(en, (Language.RU,))}')
        print(f'en-ru — {await t.translate(en, Language.EN, Language.RU)}')

    print(f'{ru} — {await async_detect(ru)}')
    print(f'ru-en — {await async_translate(ru)}')

    print(f'поддерживаемые языки: {Translator.supported_langs}')

    print(f'supported langs: {get_supported_langs()}')


if __name__ == '__main__':
    import asyncio

    asyncio.run(use())
```
