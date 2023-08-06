import logging
from os import environ
from pathlib import Path
from tempfile import gettempdir
from typing import Any, Dict, Union

from pydantic import BaseSettings, DirectoryPath, Field, validator


class Settings(BaseSettings):
    env_prefix: str
    cache_shard: int = 8
    cache_timeout: float = 0.1
    lock_key: str
    cache_dir: DirectoryPath
    expire: float = 60 * 60 * 24  # 24시간
    lock_expire: float = 10
    log_level: str = "INFO"

    @validator("log_level", pre=True)
    def set_log_level(cls, v: str) -> str:
        logger = logging.getLogger(__package__)
        logger.setLevel(v)
        return v


class OuterSettings(BaseSettings):
    default_env_prefix: str = "PYEASYCACHE_"

    @validator("default_env_prefix", pre=True)
    def set_upper_default(cls, v: str) -> str:
        return v.upper()

    env_prefix: str = Field(None)

    @validator("env_prefix", pre=True)
    def get_env_prefix(cls, v: Any, values: Dict[str, Any]):
        default = values["default_env_prefix"]
        return environ.setdefault("PYEASYCACHE_ENV_PREFIX", default).upper()

    def create_inner_settings(self) -> Settings:
        if hasattr(self, "_inner_settings"):
            return getattr(self, "_inner_settings")

        class InnerSettings(Settings):
            env_prefix: str = self.env_prefix
            lock_key: str = self.env_prefix.lower() + "lock"
            cache_dir: DirectoryPath = Field(
                f"{gettempdir()}/{self.env_prefix.lower()}cache"
            )

            @validator("cache_dir", pre=True)
            def touch_cache_dir(cls, v: Union[str, Path]) -> Union[str, Path]:
                if isinstance(v, str):
                    path = Path(v).resolve()
                else:
                    path = v.resolve()

                path.mkdir(parents=False, exist_ok=True)

                return v

            class Config:
                env_prefix = self.env_prefix
                case_sensitive = False

        inner_settings = InnerSettings()  # type: ignore
        object.__setattr__(self, "_inner_settings", inner_settings)
        return inner_settings


outer_settings = OuterSettings()  # type: ignore
settings = outer_settings.create_inner_settings()
