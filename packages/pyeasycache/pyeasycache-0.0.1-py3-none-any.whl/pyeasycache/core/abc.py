import logging
from abc import ABC, abstractmethod
from inspect import iscoroutinefunction
from typing import (
    Any,
    AsyncContextManager,
    Callable,
    ContextManager,
    Coroutine,
    Generic,
    Protocol,
    Set,
    TypeVar,
    Union,
    overload,
)

from diskcache import ENOVAL
from typing_extensions import ParamSpec, Self

logger = logging.getLogger(__package__)

_P = ParamSpec("_P")
_Key = TypeVar("_Key")
_KeyC = TypeVar("_KeyC", covariant=True)
_R = TypeVar("_R")
_RC = TypeVar("_RC", covariant=True)
CacheType = TypeVar("CacheType", bound=Union["SyncCache", "AsyncCache"])
NoneStr = Union[str, None]
NoneNum = Union[float, None]
IgnoreSet = Set[Union[str, int]]
NoneIgnoreSet = Union[IgnoreSet, None]


def is_coro_func(func: Callable):
    is_coro = hasattr(func, "is_coro_func") and func.is_coro_func
    return is_coro or iscoroutinefunction(func)


class CacheMeta(ABC, Generic[_Key]):
    @abstractmethod
    def __getitem__(self, key: _Key) -> Any:
        ...

    @abstractmethod
    def __setitem__(self, key: _Key, value: Any) -> Any:
        ...

    @abstractmethod
    def __delitem__(self, key: _Key) -> Any:
        ...

    def __contains__(self, key: _Key) -> bool:
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True


class SyncCache(CacheMeta[_Key], Generic[_Key]):
    @overload
    @abstractmethod
    def get(self, key: _Key) -> Any:
        ...

    @overload
    @abstractmethod
    def get(self, key: _Key, *, default: _R = ...) -> Union[Any, _R]:
        ...

    @abstractmethod
    def get(self, key: _Key, *, default: _R = None) -> Union[Any, _R]:
        ...

    @abstractmethod
    def set(self, key: _Key, value: Any, expire: NoneNum = None) -> Union[bool, None]:
        ...

    @abstractmethod
    def delete(self, *key: _Key) -> int:
        ...

    @abstractmethod
    def transact(self: Self) -> ContextManager[Self]:
        ...


class AsyncCache(CacheMeta[_Key], Generic[_Key]):
    @overload
    @abstractmethod
    async def get_async(self, key: _Key) -> Any:
        ...

    @overload
    @abstractmethod
    async def get_async(self, key: _Key, *, default: _R = ...) -> Union[Any, _R]:
        ...

    @abstractmethod
    async def get_async(self, key: _Key, *, default: _R = None) -> Union[Any, _R]:
        ...

    @abstractmethod
    async def set_async(
        self, key: _Key, value: Any, expire: NoneNum = None
    ) -> Union[bool, None]:
        ...

    @abstractmethod
    async def delete_async(self, *key: _Key) -> int:
        ...

    @abstractmethod
    def transact_async(self: Self) -> AsyncContextManager[Self]:
        ...


class Cache(SyncCache[_Key], AsyncCache[_Key], Generic[_Key]):
    ...


class CacheFunc(Protocol, Generic[_P, _RC, _KeyC]):
    def __cache_key__(self, *args: _P.args, **kwargs: _P.kwargs) -> _KeyC:
        ...

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _RC:
        ...


class EverDecorator:
    @classmethod
    @property
    def decorator_name(cls) -> str:
        return cls.__name__

    def create_sync_wrapper(self, func: Callable[_P, _R]) -> Callable[_P, _R]:
        raise NotImplementedError

    def create_async_wrapper(
        self, func: Callable[_P, Coroutine[Any, Any, _R]]
    ) -> Callable[_P, Coroutine[Any, Any, _R]]:
        raise NotImplementedError

    def __call__(self, func: Callable[_P, _R]) -> Callable[_P, _R]:
        logger.debug(f"ever decorator target: {type(func)=}, {func.__name__}")

        if is_coro_func(func):
            logger.debug(
                f"coro func {func.__name__} is decorated by {self.decorator_name}"
            )
            return self.create_async_wrapper(func)  # type: ignore
            # return wraps(func)(self.create_async_wrapper(func))  # type: ignore

        logger.debug(
            f"non coro func {func.__name__} is decorated by {self.decorator_name}"
        )
        return self.create_sync_wrapper(func)
        # return wraps(func)(self.create_sync_wrapper(func))


class WrapperWithoutInit(Generic[_P, _R]):
    __name__: str
    __qualname__: str
    __module__: str
    __call__: Callable

    def cache_key(self, *args: _P.args, **kwargs: _P.kwargs) -> Any:
        raise NotImplementedError

    def __cache_key__(self, *args: _P.args, **kwargs: _P.kwargs) -> Any:
        return self.cache_key(*args, **kwargs)

    def set_attr(self, attr: str, target: Any, default: Any):
        setattr(self, attr, getattr(target, attr, getattr(self, attr, default)))

    def post_init(self):
        func = getattr(self, "func", None)
        for attr in ("__name__", "__qualname__", "__module__"):
            self.set_attr(attr, func, "")

    @property
    def is_coro_func(self):
        return iscoroutinefunction(self.__call__)


class WrapperMeta(WrapperWithoutInit[_P, _R], Generic[_P, _R, CacheType]):
    def __init__(
        self,
        cache: CacheType,
        func: Union[Callable[_P, _R], Callable[_P, Coroutine[Any, Any, _R]]],
        expire: NoneNum,
    ):
        self.cache = cache
        self.func = func
        self.expire = expire
        self.post_init()


class SyncDecoWrapper(WrapperMeta[_P, _R, SyncCache], Generic[_P, _R]):
    func: Callable[_P, _R]

    def __init__(
        self,
        cache: SyncCache,
        func: Callable[_P, _R],
        expire: NoneNum,
    ):
        if is_coro_func(func):
            raise TypeError(f"{func.__name__} is not sync func")
        super().__init__(cache, func, expire)

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        key = self.__cache_key__(*args, **kwargs)
        logger.debug(f"get from cache as sync: {type(self.func)=}")
        result = self.cache.get(key, default=ENOVAL)
        if result is not ENOVAL:
            return result  # type: ignore

        result = self.func(*args, **kwargs)
        self.cache.set(key, result, self.expire)
        return result


class SyncDecoWrapperForAsync(WrapperMeta[_P, _R, SyncCache], Generic[_P, _R]):
    func: Callable[_P, Coroutine[Any, Any, _R]]

    def __init__(
        self,
        cache: SyncCache,
        func: Callable[_P, Coroutine[Any, Any, _R]],
        expire: NoneNum,
    ):
        if not is_coro_func(func):
            raise TypeError(f"{func.__name__} is not async func")
        super().__init__(cache, func, expire)

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        logger.warning("use sync cache for async func")

        key = self.__cache_key__(*args, **kwargs)
        result = self.cache.get(key, default=ENOVAL)
        if result is not ENOVAL:
            return result  # type: ignore

        result = await self.func(*args, **kwargs)
        self.cache.set(key, result, self.expire)
        return result


class AsyncDecoWrapper(WrapperMeta[_P, _R, AsyncCache], Generic[_P, _R]):
    func: Callable[_P, Coroutine[Any, Any, _R]]

    def __init__(
        self,
        cache: AsyncCache,
        func: Callable[_P, Coroutine[Any, Any, _R]],
        expire: NoneNum,
    ):
        if not is_coro_func(func):
            raise TypeError(f"{func.__name__} is not async func")
        super().__init__(cache, func, expire)

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        key = self.__cache_key__(*args, **kwargs)
        result = await self.cache.get_async(key, default=ENOVAL)
        if result is not ENOVAL:
            return result  # type: ignore

        result = await self.func(*args, **kwargs)
        await self.cache.set_async(key, result, self.expire)
        return result


class AsyncDecoWrapperForSync(WrapperMeta[_P, _R, AsyncCache], Generic[_P, _R]):
    func: Callable[_P, _R]

    def __init__(
        self,
        cache: AsyncCache,
        func: Callable[_P, _R],
        expire: NoneNum,
    ):
        if not is_coro_func(func):
            raise TypeError(f"{func.__name__} is not sync func")
        super().__init__(cache, func, expire)

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        logger.warning("use async cache for sync func")

        key = self.__cache_key__(*args, **kwargs)
        result = await self.cache.get_async(key, default=ENOVAL)
        if result is not ENOVAL:
            return result  # type: ignore

        result = self.func(*args, **kwargs)
        await self.cache.set_async(key, result, self.expire)
        return result


class CachedFuncDecorator(Protocol, Generic[_KeyC]):
    # EverDecorator: FuncDecorator
    @overload
    def __call__(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, _KeyC]:
        ...

    @overload
    def __call__(
        self, func: Callable[_P, Coroutine[Any, Any, _R]]
    ) -> CacheFunc[_P, Coroutine[Any, Any, _R], _KeyC]:
        ...

    def __call__(self, func: Callable[_P, _R]) -> CacheFunc[_P, _R, _KeyC]:
        ...


class CacheMemoize(EverDecorator, Generic[_Key]):
    @abstractmethod
    def memoize(
        self,
        name: NoneStr = ...,
        typed: bool = ...,
        expire: NoneNum = ...,
        ignore: NoneIgnoreSet = ...,
    ) -> CachedFuncDecorator[_Key]:
        ...


class CacheFuncDecorator(Protocol, Generic[_KeyC]):
    def __call__(
        self,
        name: NoneStr = ...,
        typed: bool = ...,
        expire: NoneNum = ...,
        ignore: NoneIgnoreSet = ...,
    ) -> CachedFuncDecorator[_KeyC]:
        ...


class CacheDecorator(ABC, Generic[_Key]):
    def method(
        self,
        name: NoneStr = None,
        typed: bool = False,
        expire: NoneNum = None,
        ignore: NoneIgnoreSet = None,
    ) -> CachedFuncDecorator[_Key]:
        return self(name, typed, expire, ignore, is_method=True)

    @abstractmethod
    def __call__(
        self,
        name: NoneStr = None,
        typed: bool = False,
        expire: NoneNum = None,
        ignore: NoneIgnoreSet = None,
        is_method: bool = False,
    ) -> CachedFuncDecorator:
        ...


class SyncLock(Protocol):
    acquire: Callable[..., Any]
    release: Callable[..., Any]
    __enter__: Callable[..., Any]
    __exit__: Callable[..., Any]


class AsyncLock(Protocol):
    acquire: Callable[..., Coroutine[Any, Any, Any]]
    release: Callable[..., Coroutine[Any, Any, Any]]
    __aenter__: Callable[..., Coroutine[Any, Any, Any]]
    __aexit__: Callable[..., Coroutine[Any, Any, Any]]


class CacheKeyConverter(ABC, Generic[_P, _Key]):
    cache_key: Union[Callable[_P, _Key], None]

    def __init__(
        self,
        func: Callable[_P, Any],
        cache_key: Union[Callable[_P, _Key], None],
        **kwargs: Any,
    ):
        logger.debug(f"create cache key converter: {type(func)=} {func.__name__}")
        self.func = func
        self.cache_key = cache_key
        self.kwargs = kwargs

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _Key:
        if self.cache_key is None:
            return self.none(*args, **kwargs)
        return self.call(*args, **kwargs)

    @abstractmethod
    def get_cache_key(self) -> Callable[_P, _Key]:
        ...

    @abstractmethod
    def call(self, *args: _P.args, **kwargs: _P.kwargs) -> _Key:
        ...

    @abstractmethod
    def none(self, *args: _P.args, **kwargs: _P.kwargs) -> _Key:
        ...


class LockWarpperMeta(WrapperWithoutInit[_P, _R], Generic[_P, _R]):
    cache_key: CacheKeyConverter[_P, Any]

    def __init__(
        self,
        func: Union[Callable[_P, _R], Callable[_P, Coroutine[Any, Any, _R]]],
        lock_builder: Union[Callable[[Any], SyncLock], Callable[[Any], AsyncLock]],
    ):
        self.func = func
        self.lock_builder = lock_builder
        self.post_init()


class SyncLockWrapper(LockWarpperMeta[_P, _R], Generic[_P, _R]):
    func: Callable[_P, _R]
    lock_builder: Callable[[Any], SyncLock]

    def __init__(
        self,
        func: Callable[_P, _R],
        lock_builder: Callable[[Any], SyncLock],
    ):
        logger.debug(f"init start sync lock wrapper: {type(func)=}, {id(func)=}")
        super().__init__(func, lock_builder)
        logger.debug(
            f"init end sync lock wrapper: {type(self.func)=}, {id(self.func)=}"
        )

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        logger.debug(
            f"call func in sync lock wrapper: {type(self.func)=}, {id(self.func)=}"
        )
        key = self.__cache_key__(*args, **kwargs)
        lock = self.lock_builder(key)
        with lock:
            return self.func(*args, **kwargs)


class SyncLockWrapperForAsync(LockWarpperMeta[_P, _R], Generic[_P, _R]):
    func: Callable[_P, Coroutine[Any, Any, _R]]
    lock_builder: Callable[[Any], SyncLock]

    def __init__(
        self,
        func: Callable[_P, Coroutine[Any, Any, _R]],
        lock_builder: Callable[[Any], SyncLock],
    ):
        super().__init__(func, lock_builder)

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        logger.warning("use sync Lock for async func")

        key = self.cache_key(*args, **kwargs)
        lock = self.lock_builder(key)
        with lock:
            return await self.func(*args, **kwargs)


class AsyncLockWrapper(LockWarpperMeta[_P, _R], Generic[_P, _R]):
    func: Callable[_P, Coroutine[Any, Any, _R]]
    lock_builder: Callable[[Any], AsyncLock]

    def __init__(
        self,
        func: Callable[_P, Coroutine[Any, Any, _R]],
        lock_builder: Callable[[Any], AsyncLock],
    ):
        super().__init__(func, lock_builder)

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        key = self.__cache_key__(*args, **kwargs)
        lock = self.lock_builder(key)
        async with lock:
            return await self.func(*args, **kwargs)


class AsyncLockWrapperForSync(LockWarpperMeta[_P, _R], Generic[_P, _R]):
    func: Callable[_P, _R]
    lock_builder: Callable[[Any], AsyncLock]

    def __init__(
        self,
        func: Callable[_P, _R],
        lock_builder: Callable[[Any], AsyncLock],
    ):
        super().__init__(func, lock_builder)

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        logger.warning("use async Lock for sync func")

        key = self.__cache_key__(*args, **kwargs)
        lock = self.lock_builder(key)
        async with lock:
            return self.func(*args, **kwargs)


class Barrier(ABC):
    @abstractmethod
    def create_lock(self, name: Any, expire: NoneNum = None) -> SyncLock:
        ...

    @abstractmethod
    def create_lock_async(self, name: Any, expire: NoneNum = None) -> AsyncLock:
        ...

    @abstractmethod
    def __call__(
        self, name: NoneStr = None, expire: NoneNum = None, is_method: bool = False
    ) -> EverDecorator:
        ...


class CacheDeleteCallback(Protocol):
    def __call__(self, obj: Any, /) -> bool:
        ...


class CacheDeleteCallbackDecorator(ABC, Generic[_Key]):
    @abstractmethod
    def __call__(self, callback: CacheDeleteCallback) -> CachedFuncDecorator[_Key]:
        ...


class CallbackWarpperMeta(WrapperWithoutInit[_P, _R], Generic[_P, _R, CacheType]):
    def __init__(
        self,
        cache: CacheType,
        func: Union[Callable[_P, _R], Callable[_P, Coroutine[Any, Any, _R]]],
        callback: CacheDeleteCallback,
    ):
        self.cache = cache
        self.func = func
        self.callback = callback
        self.post_init()


class SyncCallbackWrapper(CallbackWarpperMeta[_P, _R, SyncCache], Generic[_P, _R]):
    func: Callable[_P, _R]

    def __init__(
        self, cache: SyncCache, func: Callable[_P, _R], callback: CacheDeleteCallback
    ):
        super().__init__(cache, func, callback)

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        result = self.func(*args, **kwargs)
        if self.callback(result):
            key = self.__cache_key__(*args, **kwargs)
            with self.cache.transact() as cache:
                cache.delete(key)
        return result


class SyncCallbackWrapperForAsync(
    CallbackWarpperMeta[_P, _R, SyncCache], Generic[_P, _R]
):
    func: Callable[_P, Coroutine[Any, Any, _R]]

    def __init__(
        self,
        cache: SyncCache,
        func: Callable[_P, Coroutine[Any, Any, _R]],
        callback: CacheDeleteCallback,
    ):
        super().__init__(cache, func, callback)

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        logger.warning("use sync cache for async func")

        result = await self.func(*args, **kwargs)
        if self.callback(result):
            key = self.__cache_key__(*args, **kwargs)
            with self.cache.transact() as cache:
                cache.delete(key)
        return result


class AsyncCallbackWrapper(CallbackWarpperMeta[_P, _R, AsyncCache], Generic[_P, _R]):
    func: Callable[_P, Coroutine[Any, Any, _R]]

    def __init__(
        self,
        cache: AsyncCache,
        func: Callable[_P, Coroutine[Any, Any, _R]],
        callback: CacheDeleteCallback,
    ):
        super().__init__(cache, func, callback)

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        result = await self.func(*args, **kwargs)
        if self.callback(result):
            key = self.__cache_key__(*args, **kwargs)
            async with self.cache.transact_async() as cache:
                await cache.delete_async(key)
        return result


class AsyncCallbackWrapperForSync(
    CallbackWarpperMeta[_P, _R, AsyncCache], Generic[_P, _R]
):
    func: Callable[_P, _R]

    def __init__(
        self,
        cache: AsyncCache,
        func: Callable[_P, _R],
        callback: CacheDeleteCallback,
    ):
        super().__init__(cache, func, callback)

    async def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        logger.warning("use async cache for sync func")

        result = self.func(*args, **kwargs)
        if self.callback(result):
            key = self.__cache_key__(*args, **kwargs)
            async with self.cache.transact_async() as cache:
                await cache.delete_async(key)
        return result
