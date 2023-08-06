import time
import unittest

import mock

import mopidy_waitfortimesync

import mopidy_waitforinternet


class WaitForTimeSyncExtensionTest(unittest.TestCase):

    def setUp(self):
        self.backup_check_urls = mopidy_waitforinternet.check_urls

    def test01_get_default_config(self):
        ext = mopidy_waitfortimesync.WaitForTimeSyncExtension()

        config = ext.get_default_config()

        self.assertIn('[waitfortimesync]', config)
        self.assertIn('enabled = false', config)

    def test02_setup_realrun(self):
        registry = mock.Mock()

        ext = mopidy_waitfortimesync.WaitForTimeSyncExtension()

        t_start = time.monotonic()
        ext.setup(registry)
        t_stop = time.monotonic()

        registry.add.assert_not_called()
        self.assertGreater(t_stop - t_start, 0)
        self.assertLess(t_stop - t_start, 0.999)

    def tearDown(self):
        mopidy_waitforinternet.check_urls = self.backup_check_urls
