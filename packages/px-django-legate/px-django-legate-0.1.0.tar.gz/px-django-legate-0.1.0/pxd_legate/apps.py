from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ('LegateConfig',)


class LegateConfig(AppConfig):
    name = 'pxd_legate'
    verbose_name = pgettext_lazy('pxd_legate', 'Legate')
