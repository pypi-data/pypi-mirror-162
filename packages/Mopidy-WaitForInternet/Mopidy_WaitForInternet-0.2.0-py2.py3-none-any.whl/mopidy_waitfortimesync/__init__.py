import logging
import os

from mopidy import config, ext

import mopidy_waitforinternet

__version__ = mopidy_waitforinternet.__version__

logger = logging.getLogger(__name__)


class WaitForTimeSyncExtension(ext.Extension):
    dist_name = 'Mopidy-WaitForInternet'
    ext_name = 'waitfortimesync'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def setup(self, registry):
        mopidy_waitforinternet.WaitForInternetExtension.wait_for_internet(True, logger)
