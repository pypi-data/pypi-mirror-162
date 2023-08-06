import logging
from contextlib import ExitStack, contextmanager
from functools import partial
from itertools import groupby
from pickle import UnpicklingError
from typing import (
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    Iterator,
    List,
    Type,
    TypeVar,
    Union,
    final,
    overload,
)

from pottery.redlock import Redlock
from pydantic import BaseModel
from pyeasycache.backend.redis.types import KeyType
from pyeasycache.core import settings
from pyeasycache.core.abc import AsyncLock, Barrier, CacheDecorator
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
    from_pickle,
    lock_wrapper_factory,
    to_pickle,
)
from typing_extensions import Literal, ParamSpec, Self

from redis.asyncio.client import Pipeline as AsyncPipe
from redis.client import Pipeline as SyncPipe
from redis.client import Redis as SyncRedis
from redis.cluster import RedisCluster as SyncCluster

_P = ParamSpec("_P")
_R = TypeVar("_R")
_Key = TypeVar("_Key", bound=KeyType)
_SyncRedis = TypeVar("_SyncRedis", bound=Union[SyncRedis, SyncCluster])
_SyncRedisOrPipe = TypeVar(
    "_SyncRedisOrPipe", bound=Union[SyncRedis, SyncPipe, SyncCluster]
)
# _AsyncRedis = TypeVar("_AsyncRedis", bound=Union[AsyncRedis, AsyncCluster])
# _AsyncRedisOrPipe = TypeVar(
#     "_AsyncRedisOrPipe", bound=Union[AsyncRedis, AsyncPipe, AsyncCluster]
# )
logger = logging.getLogger(__package__)


class RedisCacheMemoizeDecorator(EverDecorator, Generic[_P]):
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
            cache_key = cache_key_func_builder(
                func, self.name, self.typed, self.ignore, dump=True
            )
        else:
            cache_key = self.cache_key
        return cache_key

    def create_async_wrapper(
        self, func: Callable[_P, Coroutine[Any, Any, _R]]
    ) -> CacheFunc[_P, Coroutine[Any, Any, _R], KeyType]:
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


class RedisPool(Generic[_SyncRedisOrPipe, _Key]):
    # class RedisPool(Generic[_SyncRedisOrPipe, _AsyncRedisOrPipe, _Key]):
    sync_pool: List[_SyncRedisOrPipe]
    # async_pool: List[_AsyncRedisOrPipe]

    def __len__(self):
        return len(self.sync_pool)
        # return len(self.sync_pool) or len(self.async_pool)

    def index(self, key: _Key) -> int:
        return hash(key) % len(self)

    @overload
    @staticmethod
    def get_expire(expire: NoneNum, multi: int = ...) -> int:
        ...

    @overload
    @staticmethod
    def get_expire(
        expire: NoneNum, multi: int = ..., return_type: Type[int] = ...
    ) -> int:
        ...

    @overload
    @staticmethod
    def get_expire(
        expire: NoneNum, multi: int = ..., return_type: Type[float] = ...
    ) -> float:
        ...

    @overload
    @staticmethod
    def get_expire(
        expire: NoneNum,
        multi: int = ...,
        return_type: Union[Type[int], Type[float]] = ...,
    ) -> Union[float, int]:
        ...

    @staticmethod
    def get_expire(
        expire: NoneNum,
        multi: int = 1000,
        return_type: Union[Type[int], Type[float]] = int,
    ) -> Union[float, int]:
        expire = settings.expire if expire is None else expire
        if expire <= 0 and return_type is int:
            return 1
        return return_type(expire * multi)

    # @overload
    # def get_core(self, key: _Key) -> _SyncRedisOrPipe:
    #     ...

    # @overload
    # def get_core(self, key: _Key, is_async: Literal[False] = ...) -> _SyncRedisOrPipe:
    #     ...

    # @overload
    # def get_core(self, key: _Key, is_async: Literal[True] = ...) -> _AsyncRedisOrPipe:
    #     ...

    # @overload
    # def get_core(
    #     self, key: _Key, is_async: bool = ...
    # ) -> Union[_SyncRedisOrPipe, _AsyncRedisOrPipe]:
    #     ...

    def get_core(self, key: _Key) -> _SyncRedisOrPipe:
        #     self, key: _Key, is_async: bool = False
        # ) -> Union[_SyncRedisOrPipe, _AsyncRedisOrPipe]:
        index = self.index(key)
        return self.sync_pool[index]
        # if is_async:
        #     return self.async_pool[index]
        # else:
        #     return self.sync_pool[index]


class RedisPipePool(RedisPool[SyncPipe, _Key], Generic[_Key]):
    # class RedisPipePool(RedisPool[SyncPipe, AsyncPipe, _Key], Generic[_Key]):
    def __init__(self, sync_pool: List[SyncPipe]) -> None:
        # def __init__(self, sync_pool: List[SyncPipe], async_pool: List[AsyncPipe]) -> None:
        self.sync_pool = sync_pool
        # self.async_pool = async_pool

    def replace_pipe(
        self,
        key: Union[int, _Key],
        pipe: Union[SyncPipe, AsyncPipe],
        # is_async: Union[bool, None] = None,
        is_index: bool = False,
    ):
        # if is_async is None:
        #     is_async = isinstance(pipe, AsyncPipe)

        int_key = isinstance(key, int)
        index: int
        if is_index:
            if not int_key:
                raise TypeError("is_index=True but key is not int")
            index = key
        else:
            if int_key:
                raise TypeError("is_index=False but key is int")
            index = self.index(key)

        self.sync_pool[index] = pipe  # type: ignore
        # if is_async:
        #     self.async_pool[index] = pipe  # type: ignore
        # else:
        #     self.sync_pool[index] = pipe  # type: ignore

    def get(self, key: _Key) -> Self:
        pipe = self.get_core(key)
        pipe = pipe.get(key)
        self.replace_pipe(key, pipe)
        # self.replace_pipe(key, pipe, is_async=False)
        return self

    def set(self, key: _Key, value: Any, expire: NoneNum = None) -> Self:
        px = self.get_expire(expire)
        pipe = self.get_core(key)
        pipe = pipe.set(key, value, px=px)
        self.replace_pipe(key, pipe)
        # self.replace_pipe(key, pipe, is_async=False)
        return self

    def delete(self, *key: _Key) -> Self:
        with_index = zip(map(self.index, key), key)
        key_group = groupby(with_index, key=lambda tup: tup[0])

        for index, group in key_group:
            pipe = self.sync_pool[index]
            keys = (_key[1] for _key in group)
            pipe = pipe.delete(*keys)
            self.replace_pipe(index, pipe, is_index=True)
            # self.replace_pipe(index, pipe, is_async=False, is_index=True)

        return self

    def execute(self):
        return [pipe.execute() for pipe in self.sync_pool]

    # async def get_async(self, key: _Key) -> Self:
    #     pipe = self.get_core(key, is_async=True)
    #     pipe = await pipe.get(key)
    #     self.replace_pipe(key, pipe, is_async=True)  # type: ignore
    #     return self

    # async def set_async(self, key: _Key, value: Any, expire: NoneNum = None) -> Self:
    #     px = self.get_expire(expire)
    #     pipe = self.get_core(key, is_async=True)
    #     pipe = await pipe.set(key, value, px=px)
    #     self.replace_pipe(key, pipe, is_async=True)  # type: ignore
    #     return self

    # async def delete_async(self, *key: _Key) -> Self:
    #     with_index = zip(map(self.index, key), key)
    #     key_group = groupby(with_index, key=lambda tup: tup[0])

    #     for index, group in key_group:
    #         pipe = self.async_pool[index]
    #         keys = (_key[1] for _key in group)
    #         pipe = await pipe.delete(*keys)
    #         self.replace_pipe(index, pipe, is_async=True, is_index=True)  # type: ignore
    #     return Self

    # async def execute_async(self):
    #     return [await pipe.execute() for pipe in self.async_pool]


class RedisCachePool(
    SyncCache[_Key], RedisPool[_SyncRedis, _Key], Generic[_SyncRedis, _Key]
):
    # class RedisCachePool(
    #     Cache[_Key],
    #     RedisPool[_SyncRedis, _AsyncRedis, _Key],
    #     Generic[_SyncRedis, _AsyncRedis, _Key],
    # ):
    def __init__(self, sync_pool: List[_SyncRedis]) -> None:
        #     self, sync_pool: List[_SyncRedis], async_pool: List[_AsyncRedis]
        # ) -> None:
        self.sync_pool = sync_pool
        # self.async_pool = async_pool

    @classmethod
    def from_urls(
        cls: Type[Self],
        *urls: str,
        redis_class: Type[_SyncRedis],
        # sync_class: Type[_SyncRedis],
        # async_class: Type[_AsyncRedis],
        **kwargs: Any,
    ) -> Self:
        sync_pool = [redis_class.from_url(url, **kwargs) for url in urls]
        # sync_pool = [sync_class.from_url(url, **kwargs) for url in urls]
        # async_pool = [async_class.from_url(url, **kwargs) for url in urls]
        return cls(sync_pool)
        # return cls(sync_pool, async_pool)

    def __getitem__(self, key: _Key) -> Any:
        redis = self.get_core(key)
        if (data := redis.get(key)) is None:
            raise KeyError(key)
        return decode_stored_value(data)

    def __setitem__(self, key: _Key, value: Any) -> Union[bool, None]:
        redis = self.get_core(key)
        data = encode_value_for_store(value)
        return redis.set(key, data)

    def __delitem__(self, key: _Key) -> int:
        redis = self.get_core(key)
        return redis.delete(key)

    def __contains__(self, key: _Key) -> bool:
        redis = self.get_core(key)
        return bool(redis.exists(key))

    def get(self, key: _Key, *, default: Any = None):
        redis = self.get_core(key)
        if (data := redis.get(key)) is None:
            return default
        return decode_stored_value(data)

    def set(self, key: _Key, value: Any, expire: NoneNum = None) -> Union[bool, None]:
        px = self.get_expire(expire)
        redis = self.get_core(key)
        data = encode_value_for_store(value)
        return redis.set(key, data, px=px)

    def delete(self, *key: _Key) -> int:
        with self.transact() as pipe:
            pipe.delete(*key)
            result = pipe.execute()
        logger.debug(f"{result=}")
        return sum(x[0] for x in result)

        # with_index = zip(map(self.index, key), key)
        # key_group = groupby(with_index, key=lambda tup: tup[0])

        # result = 0
        # for index, group in key_group:
        #     redis = self.sync_pool[index]
        #     keys = (_key[1] for _key in group)
        #     result += redis.delete(*keys)
        # return result

    @contextmanager
    def transact(self: Self) -> Iterator[RedisPipePool]:
        with ExitStack() as context:
            pipes: List[SyncPipe] = [0 for _ in range(len(self))]  # type: ignore
            for num, redis in enumerate(self.sync_pool):
                pipe = redis.pipeline(transaction=False)
                pipes[num] = pipe
                context.enter_context(pipe)
            new = RedisPipePool(pipes)
            # new = RedisPipePool(pipes, [])
            yield new

    # async def get_async(self, key: _Key, *, default: Any = None):
    #     redis = self.get_core(key, is_async=True)
    #     if (data := await redis.get(key)) is None:
    #         return default
    #     return decode_stored_value(data)

    # async def set_async(
    #     self, key: _Key, value: Any, expire: NoneNum = None
    # ) -> Union[bool, None]:
    #     px = self.get_expire(expire)
    #     redis = self.get_core(key, is_async=True)
    #     data = encode_value_for_store(value)
    #     return await redis.set(key, data, px=px)

    # async def delete_async(self, *key: _Key) -> int:
    #     async with self.transact_async() as pipe:
    #         await pipe.delete_async(*key)
    #         result = await pipe.execute_async()
    #     logger.warning(f"{result=}")
    #     return sum(x[0] for x in result)

    #     with_index = zip(map(self.index, key), key)
    #     key_group = groupby(with_index, key=lambda tup: tup[0])

    #     result = 0
    #     for index, group in key_group:
    #         redis = self.async_pool[index]
    #         keys = (_key[1] for _key in group)
    #         result += await redis.delete(*keys)
    #     return result

    # @asynccontextmanager
    # async def transact_async(self: Self) -> AsyncIterator[RedisPipePool]:
    #     async with AsyncExitStack() as context:
    #         pipes: List[AsyncPipe] = [0 for _ in range(len(self))]  # type: ignore
    #         for num, redis in enumerate(self.async_pool):
    #             pipe = redis.pipeline(transaction=False)
    #             pipes[num] = pipe
    #             await context.enter_async_context(pipe)
    #         new = RedisPipePool([], pipes)
    #         yield new


@final
class RedisCache(
    RedisCachePool[_SyncRedis, KeyType],
    CacheMemoize[KeyType],
    Generic[_SyncRedis],
):
    # class RedisCache(
    #     RedisCachePool[_SyncRedis, _AsyncRedis, KeyType],
    #     CacheMemoize[KeyType],
    #     Generic[_SyncRedis, _AsyncRedis],
    # ):
    @overload
    @classmethod
    def from_urls(
        cls: Type[Self],
        *urls: str,
        is_cluster: Literal[False],
        **kwargs: Any,
    ) -> "RedisCache[SyncRedis]":
        # ) -> "RedisCache[SyncRedis, AsyncRedis]":
        ...

    @overload
    @classmethod
    def from_urls(
        cls: Type[Self],
        *urls: str,
        is_cluster: Literal[True],
        **kwargs: Any,
    ) -> "RedisCache[SyncCluster]":
        # ) -> "RedisCache[SyncCluster, AsyncCluster]":
        ...

    @overload
    @classmethod
    def from_urls(
        cls: Type[Self],
        *urls: str,
        is_cluster: bool,
        **kwargs: Any,
    ) -> "Union[RedisCache[SyncRedis ],RedisCache[SyncCluster ]]":
        # ) -> "Union[RedisCache[SyncRedis, AsyncRedis],RedisCache[SyncCluster, AsyncCluster]]":
        ...

    @classmethod
    def from_urls(
        cls: Type[Self],
        *urls: str,
        is_cluster: bool,
        **kwargs: Any,
    ) -> "Union[RedisCache[SyncRedis ],RedisCache[SyncCluster ]]":
        # ) -> "Union[RedisCache[SyncRedis, AsyncRedis],RedisCache[SyncCluster, AsyncCluster]]":
        if is_cluster:
            sync_class = SyncCluster
            # async_class = AsyncCluster
        else:
            sync_class = SyncRedis
            # async_class = AsyncRedis

        sync_pool = [sync_class.from_url(url, **kwargs) for url in urls]
        # async_pool = [async_class.from_url(url, **kwargs) for url in urls]
        return cls(sync_pool)  # type: ignore
        # return super().from_urls(
        #     *urls, sync_class=sync_class, async_class=async_class, **kwargs  # type: ignore
        # )

    def memoize(
        self,
        name: NoneStr = None,
        typed: bool = False,
        expire: NoneNum = settings.expire,
        ignore: NoneIgnoreSet = None,
        cache_key: Union[Callable[_P, KeyType], None] = None,
        cache_key_converter: Union[Type[CacheKeyConverter[_P, KeyType]], None] = None,
    ) -> CachedFuncDecorator[KeyType]:
        return RedisCacheMemoizeDecorator[_P](
            self, name, typed, expire, ignore, cache_key, cache_key_converter
        )


class RedisCacheDecorator(CacheDecorator[KeyType]):
    def __init__(self, cache: RedisCache):
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
        return RedisCacheMemoizeDecorator(self.cache, name, typed, expire, ignore)


class RedisCallbackDecorator(EverDecorator):
    def __init__(self, cache: RedisCache, callback: CacheDeleteCallbackProtocol):
        self.cache = cache
        self.callback = callback

    def create_async_wrapper(
        self, func: Callable[_P, Coroutine[Any, Any, _R]]
    ) -> CacheFunc[_P, Coroutine[Any, Any, _R], KeyType]:
        if not hasattr(func, "__cache_key__"):
            raise TypeError(f"{create_func_pk(func)} is not cached func")

        return callback_wrapper_factory(self.cache, func, self.callback)

    def create_sync_wrapper(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, KeyType]:
        if not hasattr(func, "__cache_key__"):
            raise TypeError(f"{create_func_pk(func)} is not cached func")

        return callback_wrapper_factory(self.cache, func, self.callback)

    def __call__(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, KeyType]:
        return super().__call__(func)  # type: ignore


class RedisCacheCallbackFactory(ABCCacheDeleteCallbackDecorator[KeyType]):
    def __init__(self, cache: RedisCache) -> None:
        self.cache = cache

    def __call__(
        self, callback: CacheDeleteCallbackProtocol
    ) -> CachedFuncDecorator[KeyType]:
        return RedisCallbackDecorator(self.cache, callback)


class RedisCacheKeyConverter(CacheKeyConverter[_P, KeyType], Generic[_P]):
    flag: ClassVar[str]

    def __init__(
        self,
        func: Callable[_P, Any],
        cache_key: Union[Callable[_P, _Key], None],
        **kwargs: Any,
    ):
        kwargs.pop("dump", None)
        super().__init__(func, cache_key, **kwargs)

    def call(self, *args: _P.args, **kwargs: _P.kwargs) -> KeyType:
        cache_key = self.get_cache_key()
        key = cache_key(*args, **kwargs)
        if isinstance(key, bytes):
            return key + self.flag.encode()
        else:
            return key + self.flag

    def none(self, *args: _P.args, **kwargs: _P.kwargs) -> KeyType:
        if hasattr(self, "_cache_key"):
            return getattr(self, "_cache_key")(*args, **kwargs)
        cache_key = self._cache_key = cache_key_func_builder(
            self.func, **self.kwargs, dump=True
        )
        return cache_key(*args, **kwargs)


class RedisLockCacheKeyConverter(RedisCacheKeyConverter[_P]):
    flag: ClassVar[str] = "Lock"

    def get_cache_key(self) -> Callable[_P, KeyType]:
        if (cache_key := self.cache_key) is None:
            raise AttributeError("cache_key is None")
        return cache_key


# class RedisLockBuilder(Protocol):
#     @overload
#     def __call__(self, name: KeyType) -> SyncLock:
#         ...

#     @overload
#     def __call__(self, name: KeyType, is_async: Literal[False] = ...) -> SyncLock:
#         ...

#     @overload
#     def __call__(self, name: KeyType, is_async: Literal[True] = ...) -> AsyncLock:
#         ...

#     @overload
#     def __call__(
#         self, name: KeyType, is_async: bool = ...
#     ) -> Union[SyncLock, AsyncLock]:
#         ...

#     def __call__(
#         self, name: KeyType, is_async: bool = False
#     ) -> Union[SyncLock, AsyncLock]:
#         ...


class RedisLockDecorator(EverDecorator):
    def __init__(
        self,
        lock_builder: Callable[[KeyType], SyncLock],
        # lock_builder: RedisLockBuilder,
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
        ignore = self.get_ignore_set(self.ignore)

        cache_key = cache_key_func_builder(func, self.name, False, ignore, dump=True)
        # lock_builder = partial(self.lock_builder, is_async=True)
        return lock_wrapper_factory(
            func,
            cache_key,
            RedisLockCacheKeyConverter,
            self.lock_builder,
            # lock_builder,
            "test",
            name=self.name,
            ignore=self.ignore,
        )

    def create_sync_wrapper(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, KeyType]:
        ignore = self.get_ignore_set()
        logger.debug(f"sync lock wrapper target: {type(func)=}, {create_func_pk(func)}")

        cache_key = cache_key_func_builder(func, self.name, False, ignore, dump=True)
        # lock_builder = partial(self.lock_builder, is_async=False)
        return lock_wrapper_factory(
            func,
            cache_key,
            RedisLockCacheKeyConverter,
            self.lock_builder,
            # lock_builder,
            "test",
            name=self.name,
            ignore=self.ignore,
        )

    def __call__(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, KeyType]:
        return super().__call__(func)  # type: ignore


# class AsyncRedisLock:
#     def __init__(
#         self,
#         key: str,
#         async_pool: List[Union[AsyncRedis, AsyncCluster]],
#         expire: float,
#     ) -> None:
#         self.key = key
#         self.async_pool = async_pool
#         self.expire = expire

#     def create_manager(self) -> Aioredlock:
#         return Aioredlock(self.async_pool)  # type: ignore

#     async def acquire(self, expire: NoneNum = None):
#         manager = self.manager = self.create_manager()
#         lock = self.lock = await manager.lock(self.key, expire or self.expire)
#         return lock

#     async def release(self):
#         if not hasattr(self, "manager") or not hasattr(self, "lock"):
#             raise AttributeError("need acquire")

#         await self.manager.unlock(self.lock)
#         del self.lock
#         del self.manager

#     async def __aenter__(self, expire: NoneNum = None):
#         return await self.acquire(expire)

#     async def __aexit__(self):
#         await self.release()


class RedisBarrier(Barrier):
    def __init__(self, cache: RedisCache) -> None:
        self.cache = cache

    @staticmethod
    def get_lock_expire(expire: NoneNum):
        return settings.lock_expire if expire is None else expire

    def create_lock(self, name: KeyType, expire: NoneNum = None) -> SyncLock:
        return Redlock(
            key=name,  # type: ignore
            masters=self.cache.sync_pool,
            auto_release_time=expire or settings.lock_expire,
        )

    def create_lock_async(self, name: KeyType, expire: NoneNum = None) -> AsyncLock:
        raise NotImplementedError
        # return AsyncRedisLock(
        #     name,  # type: ignore
        #     self.cache.async_pool,
        #     expire or settings.lock_expire,
        # )

    # def get_lock(
    #     self, name: KeyType, expire: NoneNum = None, is_async: bool = False
    # ) -> Union[SyncLock, AsyncLock]:
    #     if is_async:
    #         return self.create_lock_async(name, expire)
    #     else:
    #         return self.create_lock(name, expire)

    def __call__(
        self,
        name: NoneStr = None,
        expire: NoneNum = None,
        ignore: NoneIgnoreSet = None,
        is_method: bool = False,
    ) -> CachedFuncDecorator[KeyType]:
        expire = self.get_lock_expire(expire)
        lock_builder = partial(self.create_lock, expire=expire)
        # lock_builder: RedisLockBuilder = partial(self.get_lock, expire=expire)  # type: ignore
        return RedisLockDecorator(lock_builder, name, ignore, is_method)


class RedisBarrieredCacheKeyConverter(RedisCacheKeyConverter[_P]):
    flag: ClassVar[str] = "Barriered"

    def get_cache_key(self) -> Callable[_P, KeyType]:
        if (lock_cache_key := self.cache_key) is None:
            raise AttributeError("lock cache_key is None")

        if (cache_key := lock_cache_key.cache_key) is None:
            raise AttributeError("cache_key is None")

        return cache_key


class RedisBarriered(CacheDecorator[KeyType]):
    def __init__(
        self,
        cache: RedisCache,
        barrier_expire: NoneNum = None,
        barrier_ignore: NoneIgnoreSet = None,
    ) -> None:
        self.cache = cache
        self.barrier = RedisBarrier(cache)
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
        expire = self.cache.get_expire(expire, 1, float)
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
                cache_key_converter=RedisBarrieredCacheKeyConverter,
            )(second)

        return wrapper


class Capsule(BaseModel):
    data: Any


def encode_value_for_store(value: Any):
    data = Capsule(data=value)
    return to_pickle(data)


def decode_stored_value(value: Any):
    try:
        data: Capsule = from_pickle(value)
    except UnpicklingError:
        return value
    else:
        return data.data
