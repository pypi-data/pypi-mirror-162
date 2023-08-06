from dataclasses import dataclass
from px_settings.contrib.django import settings as s


__all__ = 'Settings', 'settings',


@s('pxd_legate')
@dataclass
class Settings:
    ADMIN_REGISTER_CONTENT_TYPE: bool = True
    ADMIN_REGISTER_PERMISSION: bool = True


settings = Settings()
