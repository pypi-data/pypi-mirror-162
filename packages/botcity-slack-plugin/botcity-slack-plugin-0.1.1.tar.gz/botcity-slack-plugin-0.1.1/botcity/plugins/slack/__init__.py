from .plugin import BotSlackPlugin  # noqa: F401, F403
from .models import Message, Author, Footer, Field, Color  # noqa: F401, F403

from . import _version
__version__ = _version.get_versions()['version']

