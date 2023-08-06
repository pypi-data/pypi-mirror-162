# Django
from django.apps import AppConfig

# AA Theme Console
from aa_theme_console import __version__


class AaThemeConfig(AppConfig):
    name = "aa_theme_console"
    label = "aa_theme_console"
    verbose_name = "Console like for Alliance Auth v{version}".format(
        version=__version__
    )
