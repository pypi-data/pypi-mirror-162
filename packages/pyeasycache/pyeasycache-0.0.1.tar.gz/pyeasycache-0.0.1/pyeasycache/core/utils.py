import logging
from contextlib import suppress
from functools import wraps
from pickle import HIGHEST_PROTOCOL, dumps, loads
from pickletools import optimize
from time import perf_counter
from types import TracebackType
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from diskcache.core import args_to_key, full_name
from pyeasycache.core.abc import (
    AsyncCache,
    AsyncCallbackWrapper,
    AsyncCallbackWrapperForSync,
    AsyncDecoWrapper,
    AsyncDecoWrapperForSync,
    AsyncLock,
    AsyncLockWrapper,
    AsyncLockWrapperForSync,
    CacheDeleteCallback,
    CacheKeyConverter,
    IgnoreSet,
    NoneIgnoreSet,
    NoneNum,
    NoneStr,
    SyncCache,
    SyncCallbackWrapper,
    SyncCallbackWrapperForAsync,
    SyncDecoWrapper,
    SyncDecoWrapperForAsync,
    SyncLock,
    SyncLockWrapper,
    SyncLockWrapperForAsync,
    is_coro_func,
)
from typing_extensions import Literal, ParamSpec

_P = ParamSpec("_P")
_R = TypeVar("_R")
logger = logging.getLogger(__package__)


def create_key_from_args(
    base: Tuple[str],
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    typed: bool,
    ignore: IgnoreSet,
) -> Tuple[Any, ...]:
    return args_to_key(base, args, kwargs, typed, ignore)


def create_func_pk(func: Callable) -> str:
    return full_name(func)


@overload
def cache_key_func_builder(
    func: Callable[_P, Any],
    name: NoneStr = ...,
    typed: bool = ...,
    ignore: NoneIgnoreSet = ...,
    dump: Literal[False] = ...,
) -> Callable[_P, Tuple[Any, ...]]:
    ...


@overload
def cache_key_func_builder(
    func: Callable[_P, Any],
    name: NoneStr = ...,
    typed: bool = ...,
    ignore: NoneIgnoreSet = ...,
    dump: Literal[True] = ...,
) -> Callable[_P, bytes]:
    ...


@overload
def cache_key_func_builder(
    func: Callable[_P, Any],
    name: NoneStr = ...,
    typed: bool = ...,
    ignore: NoneIgnoreSet = ...,
    dump: bool = ...,
) -> Union[Callable[_P, Tuple[Any, ...]], Callable[_P, bytes]]:
    ...


def cache_key_func_builder(
    func: Callable[_P, Any],
    name: NoneStr = None,
    typed: bool = False,
    ignore: NoneIgnoreSet = None,
    dump: bool = False,
) -> Union[Callable[_P, Tuple[Any, ...]], Callable[_P, bytes]]:
    # dickcache.core.Cache.memoize
    base = (create_func_pk(func),) if name is None else (name,)
    ignore = ignore or set()

    def cache_key(*args: _P.args, **kwargs: _P.kwargs) -> Tuple[Any, ...]:
        return create_key_from_args(base, args, kwargs, typed, ignore)

    if dump:
        return convert_return_type_as_bytes(cache_key)

    return cache_key


def to_pickle(data: Any) -> bytes:
    new = dumps(data, protocol=HIGHEST_PROTOCOL)
    return optimize(new)


def from_pickle(data: bytes) -> Any:
    return loads(data)


def convert_return_type_as_bytes(func: Callable[_P, Any]) -> Callable[_P, bytes]:
    @wraps(func)
    def inner(*args: _P.args, **kwargs: _P.kwargs) -> bytes:
        result = func(*args, **kwargs)
        byte = dumps(result, protocol=HIGHEST_PROTOCOL)
        return optimize(byte)

    return inner


def ensure_bytes(data: Union[str, bytes]) -> bytes:
    try:
        return data.encode("utf-8")  # type: ignore
    except:
        return data  # type: ignore


def ensure_str(data: Union[str, bytes]) -> str:
    try:
        return data.decode("utf-8")  # type: ignore
    except:
        return data  # type: ignore


def arg_origin(args: tuple) -> tuple:
    return args


def arg_ignore_one(args: tuple) -> tuple:
    return args[1:]


@overload
def deco_wrapper_factory(
    cache: SyncCache,
    func: Callable[_P, Coroutine[Any, Any, _R]],
    expire: NoneNum,
    cache_key: Callable[_P, Any],
    cache_key_converter: Union[Type[CacheKeyConverter[Any, Any]], None],
    **kwargs: Any,
) -> SyncDecoWrapperForAsync[_P, _R]:
    ...


@overload
def deco_wrapper_factory(
    cache: AsyncCache,
    func: Callable[_P, Coroutine[Any, Any, _R]],
    expire: NoneNum,
    cache_key: Callable[_P, Any],
    cache_key_converter: Union[Type[CacheKeyConverter[Any, Any]], None] = ...,
    **kwargs: Any,
) -> AsyncDecoWrapper[_P, _R]:
    ...


@overload
def deco_wrapper_factory(
    cache: SyncCache,
    func: Callable[_P, _R],
    expire: NoneNum,
    cache_key: Callable[_P, Any],
    cache_key_converter: Union[Type[CacheKeyConverter[Any, Any]], None] = ...,
    **kwargs: Any,
) -> SyncDecoWrapper[_P, _R]:
    ...


@overload
def deco_wrapper_factory(
    cache: AsyncCache,
    func: Callable[_P, _R],
    expire: NoneNum,
    cache_key: Callable[_P, Any],
    cache_key_converter: Union[Type[CacheKeyConverter[Any, Any]], None] = ...,
    **kwargs: Any,
) -> AsyncDecoWrapperForSync[_P, _R]:
    ...


@overload
def deco_wrapper_factory(
    cache: Union[SyncCache, AsyncCache],
    func: Union[Callable[_P, _R], Callable[_P, Coroutine[Any, Any, _R]]],
    expire: NoneNum,
    cache_key: Callable[_P, Any],
    cache_key_converter: Union[Type[CacheKeyConverter[Any, Any]], None] = ...,
    **kwargs: Any,
) -> Union[
    SyncDecoWrapper[_P, _R],
    AsyncDecoWrapper[_P, _R],
    SyncDecoWrapperForAsync[_P, _R],
    AsyncDecoWrapperForSync[_P, _R],
]:
    ...


def deco_wrapper_factory(
    cache: Union[SyncCache, AsyncCache],
    func: Union[Callable[_P, _R], Callable[_P, Coroutine[Any, Any, _R]]],
    expire: NoneNum,
    cache_key: Callable[_P, Any],
    cache_key_converter: Union[Type[CacheKeyConverter[_P, Any]], None] = None,
    **kwargs: Any,
) -> Union[
    SyncDecoWrapper[_P, _R],
    AsyncDecoWrapper[_P, _R],
    SyncDecoWrapperForAsync[_P, _R],
    AsyncDecoWrapperForSync[_P, _R],
]:
    if cache_key_converter is not None:
        logger.debug(f"use cache_key_converter for deco: {type(cache_key)=}")
        cache_key = cache_key_converter(func, cache_key, **kwargs)

    if is_coro_func(func):
        func = cast(Callable[_P, Coroutine[Any, Any, _R]], func)
        if isinstance(cache, AsyncCache):
            wrapper = AsyncDecoWrapper(cache, func, expire)
            wrapper.cache_key = cache_key
            return wrapper
        else:
            logger.warning("use sync cache for async func")
            wrapper = SyncDecoWrapperForAsync(cache, func, expire)
            wrapper.cache_key = cache_key
            return wrapper

    func = cast(Callable[_P, _R], func)

    if isinstance(cache, SyncCache):
        wrapper = SyncDecoWrapper(cache, func, expire)
        wrapper.cache_key = cache_key
        return wrapper
    else:
        logger.warning("use async cache for sync func")
        wrapper = AsyncDecoWrapperForSync(cache, func, expire)
        wrapper.cache_key = cache_key
        return wrapper


@overload
def lock_wrapper_factory(
    func: Callable[_P, Coroutine[Any, Any, _R]],
    cache_key: Callable[_P, Any],
    cache_key_converter: Type[CacheKeyConverter[Any, Any]],
    lock_builder: Callable[[Any], SyncLock],
    test_builder_arg: Any,
    **kwargs: Any,
) -> SyncLockWrapperForAsync[_P, _R]:
    ...


@overload
def lock_wrapper_factory(
    func: Callable[_P, Coroutine[Any, Any, _R]],
    cache_key: Callable[_P, Any],
    cache_key_converter: Type[CacheKeyConverter[Any, Any]],
    lock_builder: Callable[[Any], AsyncLock],
    test_builder_arg: Any,
    **kwargs: Any,
) -> AsyncLockWrapper[_P, _R]:
    ...


@overload
def lock_wrapper_factory(
    func: Callable[_P, _R],
    cache_key: Callable[_P, Any],
    cache_key_converter: Type[CacheKeyConverter[Any, Any]],
    lock_builder: Callable[[Any], SyncLock],
    test_builder_arg: Any,
    **kwargs: Any,
) -> SyncLockWrapper[_P, _R]:
    ...


@overload
def lock_wrapper_factory(
    func: Callable[_P, _R],
    cache_key: Callable[_P, Any],
    cache_key_converter: Type[CacheKeyConverter[Any, Any]],
    lock_builder: Callable[[Any], AsyncLock],
    test_builder_arg: Any,
    **kwargs: Any,
) -> AsyncLockWrapperForSync[_P, _R]:
    ...


@overload
def lock_wrapper_factory(
    func: Union[Callable[_P, _R], Callable[_P, Coroutine[Any, Any, _R]]],
    cache_key: Callable[_P, Any],
    cache_key_converter: Type[CacheKeyConverter[Any, Any]],
    lock_builder: Union[Callable[[Any], SyncLock], Callable[[Any], AsyncLock]],
    test_builder_arg: Any,
    **kwargs: Any,
) -> Union[
    SyncLockWrapper[_P, _R],
    AsyncLockWrapper[_P, _R],
    SyncLockWrapperForAsync[_P, _R],
    AsyncLockWrapperForSync[_P, _R],
]:
    ...


def lock_wrapper_factory(
    func: Union[Callable[_P, _R], Callable[_P, Coroutine[Any, Any, _R]]],
    cache_key: Callable[_P, Any],
    cache_key_converter: Type[CacheKeyConverter[Any, Any]],
    lock_builder: Union[Callable[[Any], SyncLock], Callable[[Any], AsyncLock]],
    test_builder_arg: Any,
    **kwargs: Any,
) -> Union[
    SyncLockWrapper[_P, _R],
    AsyncLockWrapper[_P, _R],
    SyncLockWrapperForAsync[_P, _R],
    AsyncLockWrapperForSync[_P, _R],
]:
    lock = lock_builder(test_builder_arg)
    converter = cache_key_converter(func, cache_key, **kwargs)

    if is_coro_func(func):
        func = cast(Callable[_P, Coroutine[Any, Any, _R]], func)
        if hasattr(lock, "__aenter__"):
            lock_builder = cast(Callable[[Any], AsyncLock], lock_builder)
            wrapper = AsyncLockWrapper(func, lock_builder)
            wrapper.cache_key = converter
            return wrapper
        else:
            logger.warning("use sync lock for async func")

            lock_builder = cast(Callable[[Any], SyncLock], lock_builder)
            wrapper = SyncLockWrapperForAsync(func, lock_builder)
            wrapper.cache_key = converter
            return wrapper

    func = cast(Callable[_P, _R], func)
    if hasattr(lock, "__enter__"):
        lock_builder = cast(Callable[[Any], SyncLock], lock_builder)
        wrapper = SyncLockWrapper(func, lock_builder)
        wrapper.cache_key = converter
        return wrapper
    else:
        logger.warning("use async lock for sync func")

        lock_builder = cast(Callable[[Any], AsyncLock], lock_builder)
        wrapper = AsyncLockWrapperForSync(func, lock_builder)
        wrapper.cache_key = converter
        return wrapper


@overload
def callback_wrapper_factory(
    cache: SyncCache,
    func: Callable[_P, Coroutine[Any, Any, _R]],
    callback: CacheDeleteCallback,
) -> SyncCallbackWrapperForAsync[_P, _R]:
    ...


@overload
def callback_wrapper_factory(
    cache: AsyncCache,
    func: Callable[_P, Coroutine[Any, Any, _R]],
    callback: CacheDeleteCallback,
) -> AsyncCallbackWrapper[_P, _R]:
    ...


@overload
def callback_wrapper_factory(
    cache: SyncCache,
    func: Callable[_P, _R],
    callback: CacheDeleteCallback,
) -> SyncCallbackWrapper[_P, _R]:
    ...


@overload
def callback_wrapper_factory(
    cache: AsyncCache,
    func: Callable[_P, _R],
    callback: CacheDeleteCallback,
) -> AsyncCallbackWrapperForSync[_P, _R]:
    ...


@overload
def callback_wrapper_factory(
    cache: Union[SyncCache, AsyncCache],
    func: Union[Callable[_P, _R], Callable[_P, Coroutine[Any, Any, _R]]],
    callback: CacheDeleteCallback,
) -> Union[
    SyncCallbackWrapper[_P, _R],
    AsyncCallbackWrapper[_P, _R],
    SyncCallbackWrapperForAsync[_P, _R],
    AsyncCallbackWrapperForSync[_P, _R],
]:
    ...


def callback_wrapper_factory(
    cache: Union[SyncCache, AsyncCache],
    func: Union[Callable[_P, _R], Callable[_P, Coroutine[Any, Any, _R]]],
    callback: CacheDeleteCallback,
) -> Union[
    SyncCallbackWrapper[_P, _R],
    AsyncCallbackWrapper[_P, _R],
    SyncCallbackWrapperForAsync[_P, _R],
    AsyncCallbackWrapperForSync[_P, _R],
]:
    if is_coro_func(func):
        func = cast(Callable[_P, Coroutine[Any, Any, _R]], func)
        if isinstance(cache, AsyncCache):
            wrapper = AsyncCallbackWrapper(cache, func, callback)
            return wrapper
        else:
            logger.warning("use sync cache for async func")

            wrapper = SyncCallbackWrapperForAsync(cache, func, callback)
            return wrapper

    func = cast(Callable[_P, _R], func)
    if isinstance(cache, SyncCache):
        wrapper = SyncCallbackWrapper(cache, func, callback)
        return wrapper
    else:
        wrapper = AsyncCallbackWrapperForSync(cache, func, callback)
        return wrapper


class Timer:
    def __init__(self):
        self.start = perf_counter()

    @classmethod
    def tik(cls):
        return cls()

    def tok(self):
        return perf_counter() - self.start

    def __enter__(self) -> List[float]:
        self.start = perf_counter()
        self.value = [0.0]
        return self.value

    def __exit__(
        self,
        exctype: Union[Type[BaseException], None],
        excinst: Union[BaseException, None],
        exctb: Union[TracebackType, None],
    ):
        self.value[0] += self.tok()
        with suppress(AttributeError):
            del self.value
