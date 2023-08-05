from dataclasses import dataclass
from px_settings.contrib.django import settings as s


__all__ = 'Settings', 'settings',


@s('PXD_COMBINABLE_GROUPS')
@dataclass
class Settings:
    USE_LOCAL_CACHE: bool = True
    USE_DJANGO_CACHE: bool = True

    CACHE_KEY: str = 'default'
    CACHE_TIMEOUT: int = 7 * 24 * 60 * 60

    GROUP_MODEL: str = 'django.contrib.auth.models.Group'
    PERMISSION_MODEL: str = 'django.contrib.auth.models.Permission'


settings = Settings()
