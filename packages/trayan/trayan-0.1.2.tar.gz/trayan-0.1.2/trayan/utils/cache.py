from asyncio import iscoroutinefunction, ensure_future
from time import time
from typing import Optional, Callable, Union, Awaitable, Any


class cached_property:
    def __init__(self, ttl: Optional[int] = None):
        if callable(ttl):
            func = ttl
            ttl = None
        else:
            func = None
        self.ttl = ttl
        self._prepare_func(func)

    def __call__(self, func, doc=None):
        self._prepare_func(func, doc)
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self

        return self._get_cache(obj)

    def __set__(self, obj, value):
        now = time()
        if iscoroutinefunction(self.func):
            async def __coro() -> Any:
                return value

            future = ensure_future(__coro())
            self._update_cache(obj, future, now)
            return
        self._update_cache(obj, value, now)

    def __delete__(self, obj):
        obj.__dict__.pop(self.__name__, None)

    def _prepare_func(self, func: Union[Callable, Awaitable], doc: Optional[str] = None) -> None:
        self.func = func
        if func:
            self.__doc__ = doc or getattr(func, '__doc__')
            self.__name__ = func.__name__
            self.__module__ = func.__module__

    def _get_cache(self, obj: Callable) -> Any:
        now = time()
        if cache := obj.__dict__.get(self.__name__):
            cache_value, last_updated = cache
            if not (self.ttl and self.ttl < now - last_updated):
                return cache_value
        return self._create_cache(obj, now)

    def _create_cache(self, obj: Callable, now: float) -> Any:
        if iscoroutinefunction(self.func):
            async def __coro() -> Any:
                future = ensure_future(self.func(obj))
                self._update_cache(obj, future, now)
                return await future

            return __coro()
        value = self.func(obj)
        self._update_cache(obj, value, now)
        return value

    def _update_cache(self, obj: Callable, cache: Any, now: float) -> None:
        obj.__dict__[self.__name__] = (cache, now)
