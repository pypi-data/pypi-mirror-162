from .plugin import BotCrawlerPlugin  # noqa: F401, F403
from .html import HTML  # noqa: F401, F403

from . import _version
__version__ = _version.get_versions()['version']

import urllib3
urllib3.disable_warnings()
