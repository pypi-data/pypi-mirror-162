import logging
from contextlib import contextmanager
from functools import partial
from itertools import cycle
from typing import (
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    Iterator,
    Type,
    TypeVar,
    Union,
)

from diskcache import Cache as OriginDiskCache
from diskcache import Disk, FanoutCache, Lock, memoize_stampede
from pyeasycache.backend.disk.types import KeyType
from pyeasycache.core import settings
from pyeasycache.core.abc import Barrier, CacheDecorator
from pyeasycache.core.abc import CacheDeleteCallback as CacheDeleteCallbackProtocol
from pyeasycache.core.abc import (
    CacheDeleteCallbackDecorator as ABCCacheDeleteCallbackDecorator,
)
from pyeasycache.core.abc import (
    CachedFuncDecorator,
    CacheFunc,
    CacheKeyConverter,
    CacheMemoize,
    EverDecorator,
    NoneIgnoreSet,
    NoneNum,
    NoneStr,
    SyncCache,
    SyncLock,
)
from pyeasycache.core.utils import (
    cache_key_func_builder,
    callback_wrapper_factory,
    create_func_pk,
    deco_wrapper_factory,
    lock_wrapper_factory,
)
from typing_extensions import ParamSpec, Self

_P = ParamSpec("_P")
_R = TypeVar("_R")
logger = logging.getLogger(__package__)


class DiskCacheMemoizeDecorator(EverDecorator, Generic[_P]):
    def __init__(
        self,
        cache: SyncCache,
        name: NoneStr = None,
        typed: bool = False,
        expire: NoneNum = None,
        ignore: NoneIgnoreSet = None,
        cache_key: Union[Callable[_P, KeyType], None] = None,
        cache_key_converter: Union[Type[CacheKeyConverter[_P, KeyType]], None] = None,
    ) -> None:
        self.cache = cache
        self.name = name
        self.typed = typed
        self.expire = expire
        self.ignore = ignore or set()
        self.cache_key = cache_key
        self.cache_key_converter = cache_key_converter

    def get_cache_key(self, func: Callable[_P, Any]) -> Callable[_P, KeyType]:
        if self.cache_key is None:
            cache_key = cache_key_func_builder(func, self.name, self.typed, self.ignore)
        else:
            cache_key = self.cache_key
        return cache_key

    def create_async_wrapper(
        self, func: Callable[_P, Coroutine[Any, Any, _R]]
    ) -> CacheFunc[_P, Coroutine[Any, Any, _R], KeyType]:
        logger.warning("diskcache has no async method")

        cache_key = self.get_cache_key(func)
        return deco_wrapper_factory(
            self.cache, func, self.expire, cache_key, self.cache_key_converter
        )

    def create_sync_wrapper(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, KeyType]:
        cache_key = self.get_cache_key(func)
        return deco_wrapper_factory(
            self.cache, func, self.expire, cache_key, self.cache_key_converter
        )

    def __call__(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, KeyType]:
        return super().__call__(func)  # type: ignore


class DiskCache(SyncCache[KeyType], CacheMemoize[KeyType]):
    _iter_cache: Union[Iterator[OriginDiskCache], None] = None

    def __init__(
        self,
        directory: str,
        shards: int,
        timeout: float,
        disk: Type[Disk] = Disk,
        **settings: Any,
    ) -> None:
        self.fanout_cache = FanoutCache(directory, shards, timeout, disk, **settings)

    def index(self, key: KeyType) -> int:
        return self.fanout_cache._hash(key) % self.fanout_cache._count

    @property
    def iter_cache(self) -> Iterator[OriginDiskCache]:
        if self._iter_cache is not None:
            return self._iter_cache
        self._iter_cache = cycle(self.fanout_cache._shards)
        return self._iter_cache

    @staticmethod
    def get_expire(expire: NoneNum):
        return settings.expire if expire is None else expire

    def cache(self, index: Union[int, None] = None) -> OriginDiskCache:
        if index is None:
            return next(self.iter_cache)
        return self.fanout_cache._shards[index]

    def get_retry(self, key: KeyType, default: Union[Any, None] = None):
        return self.fanout_cache.get(key, default, retry=True)

    def get(self, key: KeyType, *, default: Any = None):
        return self.get_retry(key, default)

    # async def get_async(self, key: KeyType, *, default: Any = None):
    #     raise NotImplementedError
    #     return await anyio.to_thread.run_sync(self.get_retry, key, default)

    def set_retry(self, key: KeyType, value: Any, expire: NoneNum = None):
        expire = self.get_expire(expire)
        return self.fanout_cache.set(key, value, expire, retry=True)

    def set(self, key: KeyType, value: Any, expire: NoneNum = None):
        return self.set_retry(key, value, expire)

    # async def set_async(
    #     self, key: KeyType, value: Any, expire: NoneNum = settings.expire
    # ):
    #     raise NotImplementedError
    #     return await anyio.to_thread.run_sync(self.set_retry, key, value, expire)

    def delete_retry(self, *key: KeyType):
        cache = self.fanout_cache
        with cache.transact(retry=True):
            return sum([cache.delete(_key, retry=True) for _key in key])

    def delete(self, *key: KeyType):
        return self.delete_retry(*key)

    # async def delete_async(self, *key: KeyType) -> int:
    #     raise NotImplementedError
    #     return await anyio.to_thread.run_sync(self.delete_retry, *key)

    @contextmanager
    def transact(self: Self) -> Iterator[Self]:
        with self.fanout_cache.transact(retry=True):
            yield self

    # async def transact_async(self: Self) -> AsyncIterator[Self]:
    #     raise NotImplementedError

    def __getitem__(self, key: KeyType) -> Any:
        return self.fanout_cache[key]

    def __setitem__(self, key: KeyType, value: Any) -> Any:
        self.fanout_cache[key] = value

    def __delitem__(self, key: KeyType) -> Any:
        del self.fanout_cache[key]

    def memoize(
        self,
        name: NoneStr = None,
        typed: bool = False,
        expire: NoneNum = settings.expire,
        ignore: NoneIgnoreSet = None,
        cache_key: Union[Callable[_P, KeyType], None] = None,
        cache_key_converter: Union[Type[CacheKeyConverter[_P, KeyType]], None] = None,
    ) -> CachedFuncDecorator[KeyType]:
        return DiskCacheMemoizeDecorator[_P](
            self, name, typed, expire, ignore, cache_key, cache_key_converter
        )

    def memoize_stampede(
        self,
        name: NoneStr = None,
        typed: bool = False,
        expire: float = 1,
        ignore: NoneIgnoreSet = None,
        beta: int = 1,
    ) -> CachedFuncDecorator[KeyType]:
        ignore = ignore or set()
        return memoize_stampede(  # type: ignore
            self.fanout_cache, expire, name, typed, None, beta, ignore
        )


class DiskCacheDecorator(CacheDecorator[KeyType]):
    def __init__(self, cache: DiskCache):
        self.cache = cache

    def __call__(
        self,
        name: NoneStr = None,
        typed: bool = False,
        expire: NoneNum = None,
        ignore: NoneIgnoreSet = None,
        is_method: bool = False,
    ) -> CachedFuncDecorator[KeyType]:
        ignore = ignore or set()
        if is_method:
            ignore.add(0)
        return DiskCacheMemoizeDecorator(self.cache, name, typed, expire, ignore)


class DiskCallbackDecorator(EverDecorator):
    def __init__(self, cache: DiskCache, callback: CacheDeleteCallbackProtocol):
        self.cache = cache
        self.callback = callback

    def create_async_wrapper(
        self, func: Callable[_P, Coroutine[Any, Any, _R]]
    ) -> CacheFunc[_P, Coroutine[Any, Any, _R], KeyType]:
        logger.warning("diskcache has no async method")
        if not hasattr(func, "__cache_key__"):
            raise TypeError(f"{create_func_pk(func)} is not cached func")

        return callback_wrapper_factory(self.cache, func, self.callback)

    def create_sync_wrapper(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, KeyType]:
        if not hasattr(func, "__cache_key__"):
            raise TypeError(f"{create_func_pk(func)} is not cached func")

        return callback_wrapper_factory(self.cache, func, self.callback)

    def __call__(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, KeyType]:
        return super().__call__(func)  # type: ignore


class DiskCacheCallbackFactory(ABCCacheDeleteCallbackDecorator[KeyType]):
    def __init__(self, cache: DiskCache) -> None:
        self.cache = cache

    def __call__(
        self, callback: CacheDeleteCallbackProtocol
    ) -> CachedFuncDecorator[KeyType]:
        return DiskCallbackDecorator(self.cache, callback)


class DiskCacheKeyConverter(CacheKeyConverter[_P, KeyType], Generic[_P]):
    flag: ClassVar[str]

    def call(self, *args: _P.args, **kwargs: _P.kwargs) -> KeyType:
        cache_key = self.get_cache_key()
        key = cache_key(*args, **kwargs)
        return key + (self.flag,)

    def none(self, *args: _P.args, **kwargs: _P.kwargs) -> KeyType:
        if hasattr(self, "_cache_key"):
            return getattr(self, "_cache_key")(*args, **kwargs)
        cache_key = self._cache_key = cache_key_func_builder(self.func, **self.kwargs)
        return cache_key(*args, **kwargs)


class DiskLockCacheKeyConverter(DiskCacheKeyConverter[_P]):
    flag: ClassVar[str] = "Lock"

    def get_cache_key(self) -> Callable[_P, KeyType]:
        if (cache_key := self.cache_key) is None:
            raise AttributeError("cache_key is None")
        return cache_key


class DiskLockDecorator(EverDecorator):
    def __init__(
        self,
        lock_builder: Callable[[Any], SyncLock],
        name: NoneStr,
        ignore: NoneIgnoreSet,
        is_method: bool,
    ):
        # 기존 오브젝트 반복 사용하지 말고
        # 신규 오브젝트 생성 후 사용할 것
        self.lock_builder = lock_builder
        self.name = name
        self.ignore = ignore
        self.is_method = is_method

    def get_ignore_set(self, ignore: NoneIgnoreSet = None):
        ignore = ignore or set()
        ignore = ignore.copy()
        if self.is_method:
            ignore.add(0)
            return ignore
        return ignore

    def create_async_wrapper(
        self, func: Callable[_P, Coroutine[Any, Any, _R]]
    ) -> CacheFunc[_P, Coroutine[Any, Any, _R], KeyType]:
        # async 구현이 없어서 동기 lock을 신규 쓰레드에서 사용
        logger.warning("diskcache has no async lock")
        ignore = self.get_ignore_set(self.ignore)

        cache_key = cache_key_func_builder(func, self.name, False, ignore, dump=False)
        return lock_wrapper_factory(
            func,
            cache_key,
            DiskLockCacheKeyConverter,
            self.lock_builder,
            "test",
            name=self.name,
            ignore=self.ignore,
        )

    def create_sync_wrapper(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, KeyType]:
        ignore = self.get_ignore_set()
        logger.debug(f"sync lock wrapper target: {type(func)=}, {create_func_pk(func)}")

        cache_key = cache_key_func_builder(func, self.name, False, ignore, dump=False)
        return lock_wrapper_factory(
            func,
            cache_key,
            DiskLockCacheKeyConverter,
            self.lock_builder,
            "test",
            name=self.name,
            ignore=self.ignore,
        )

    def __call__(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, KeyType]:
        return super().__call__(func)  # type: ignore


class DiskBarrier(Barrier):
    def __init__(self, cache: DiskCache) -> None:
        self.cache = cache

    @staticmethod
    def get_lock_expire(expire: NoneNum):
        return settings.lock_expire if expire is None else expire

    def create_lock(self, name: KeyType, expire: NoneNum = None) -> SyncLock:
        return Lock(self.cache.fanout_cache, name, expire=expire)

    def create_lock_async(self, name: KeyType, expire: NoneNum = None):
        raise NotImplementedError

    def __call__(
        self,
        name: NoneStr = None,
        expire: NoneNum = None,
        ignore: NoneIgnoreSet = None,
        is_method: bool = False,
    ) -> CachedFuncDecorator[KeyType]:
        expire = self.get_lock_expire(expire)
        lock_builder = partial(self.create_lock, expire=expire)
        return DiskLockDecorator(lock_builder, name, ignore, is_method)


class DiskBarrieredCacheKeyConverter(DiskCacheKeyConverter[_P]):
    flag: ClassVar[str] = "Barriered"

    def get_cache_key(self) -> Callable[_P, KeyType]:
        if (lock_cache_key := self.cache_key) is None:
            raise AttributeError("lock cache_key is None")

        if (cache_key := lock_cache_key.cache_key) is None:
            raise AttributeError("cache_key is None")

        return cache_key


class DiskBarriered(CacheDecorator[KeyType]):
    def __init__(
        self,
        cache: DiskCache,
        barrier_expire: NoneNum = None,
        barrier_ignore: NoneIgnoreSet = None,
    ) -> None:
        self.cache = cache
        self.barrier = DiskBarrier(cache)
        self.expire = settings.lock_expire if barrier_expire is None else barrier_expire
        self.ignore = barrier_ignore or set()

    def __call__(
        self,
        name: NoneStr = None,
        typed: bool = False,
        expire: NoneNum = None,
        ignore: NoneIgnoreSet = None,
        is_method: bool = False,
    ) -> CachedFuncDecorator[KeyType]:
        expire = self.cache.get_expire(expire)
        if is_method:
            ignore = ignore or set()
            ignore.add(0)

        def wrapper(func: Callable[_P, _R]) -> CacheFunc[_P, _R, KeyType]:
            lock = self.barrier(
                name if name else create_func_pk(func),
                self.expire,
                is_method=is_method,
            )

            first = self.cache.memoize(name, typed, expire, ignore)(func)
            second = lock(first)
            return self.cache.memoize(
                expire=0,
                ignore=ignore,
                cache_key=getattr(second, "cache_key"),  # type: ignore
                cache_key_converter=DiskBarrieredCacheKeyConverter,
            )(second)

        return wrapper
