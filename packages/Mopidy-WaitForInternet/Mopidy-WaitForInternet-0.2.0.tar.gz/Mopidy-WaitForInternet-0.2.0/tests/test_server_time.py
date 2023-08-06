import time
import unittest

from freezegun import freeze_time

import mock

import mopidy_waitfortimesync

import responses

import mopidy_waitforinternet


@responses.activate
def TestDateHeaders(test, ext):
    responses.add(responses.GET, 'https://nosuchhost.nosuchdomain.arpa/date-header-invalid', headers={'Date': 'not a date'})
    responses.add(responses.GET, 'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-20', headers={'Date': 'Fri, 01 Jul 2022 14:00:20 GMT'})
    responses.add(responses.GET, 'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-30', headers={'Date': 'Fri, 01 Jul 2022 14:00:30 GMT'})
    responses.add(responses.GET, 'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-40', headers={'Date': 'Fri, 01 Jul 2022 14:00:40 GMT'})
    responses.add(responses.GET, 'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-50', headers={'Date': 'Fri, 01 Jul 2022 14:00:50 GMT'})
    registry = mock.Mock()

    t_start = time.monotonic()
    ext.setup(registry)
    t_stop = time.monotonic()

    registry.add.assert_not_called()
    return t_stop - t_start


class TestsWithInvalidDateHeader(unittest.TestCase):

    def setUp(self):
        self.backup_check_urls = mopidy_waitforinternet.check_urls
        mopidy_waitforinternet.check_urls = [
            'https://nosuchhost.nosuchdomain.arpa/date-header-invalid',
            'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-20',
            'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-30',
            'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-40',
            'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-50'
        ]

    def test_waitforinternet_setup_complex_actual_date(self):
        duration = TestDateHeaders(self, mopidy_waitforinternet.WaitForInternetExtension())
        self.assertGreaterEqual(duration, 0)
        self.assertLess(duration, 0.4)

    @freeze_time('2022-07-01 14:00:00', ignore=['tests'])
    def test_waitforinternet_setup_complex_at140000(self):
        duration = TestDateHeaders(self, mopidy_waitforinternet.WaitForInternetExtension())
        self.assertGreaterEqual(duration, 0)
        self.assertLess(duration, 0.4)

    @freeze_time('2022-07-01 14:00:20', ignore=['tests'])
    def test_waitforinternet_setup_complex_at140020(self):
        duration = TestDateHeaders(self, mopidy_waitforinternet.WaitForInternetExtension())
        self.assertGreaterEqual(duration, 0)
        self.assertLess(duration, 0.4)

    @freeze_time('2022-07-01 18:18:20', ignore=['tests'])
    def test_waitforinternet_setup_complex_at181820(self):
        duration = TestDateHeaders(self, mopidy_waitforinternet.WaitForInternetExtension())
        self.assertGreaterEqual(duration, 0)
        self.assertLess(duration, 0.4)

    @freeze_time('2022-07-01 14:00:20', ignore=['tests'])
    def test_waitfortimesync_setup_complex_at140020(self):
        duration = TestDateHeaders(self, mopidy_waitfortimesync.WaitForTimeSyncExtension())
        self.assertGreaterEqual(duration, 1)
        self.assertLess(duration, 1.4)

    @freeze_time('2022-07-01 14:00:35', ignore=['tests'])
    def test_waitfortimesync_setup_complex_at140035(self):
        duration = TestDateHeaders(self, mopidy_waitfortimesync.WaitForTimeSyncExtension())
        self.assertGreaterEqual(duration, 2)
        self.assertLess(duration, 2.4)

    @freeze_time('2022-07-01 14:00:59', ignore=['tests'])
    def test_waitfortimesync_setup_complex_at140059(self):
        duration = TestDateHeaders(self, mopidy_waitfortimesync.WaitForTimeSyncExtension())
        self.assertGreaterEqual(duration, 4)
        self.assertLess(duration, 4.4)

    def tearDown(self):
        mopidy_waitforinternet.check_urls = self.backup_check_urls


class TestsNoInvalidDateHeader(unittest.TestCase):

    def setUp(self):
        self.backup_check_urls = mopidy_waitforinternet.check_urls
        mopidy_waitforinternet.check_urls = [
            'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-20',
            'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-30',
            'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-40',
            'https://nosuchhost.nosuchdomain.arpa/date-header-2022-07-01-14-00-50'
        ]

    def test_waitforinternet_setup_complex_actual_date(self):
        duration = TestDateHeaders(self, mopidy_waitforinternet.WaitForInternetExtension())
        self.assertGreaterEqual(duration, 0)
        self.assertLess(duration, 0.4)

    @freeze_time('2022-07-01 14:00:00', ignore=['tests'])
    def test_waitforinternet_setup_complex_at140000(self):
        duration = TestDateHeaders(self, mopidy_waitforinternet.WaitForInternetExtension())
        self.assertGreaterEqual(duration, 0)
        self.assertLess(duration, 0.4)

    @freeze_time('2022-07-01 14:00:20', ignore=['tests'])
    def test_waitforinternet_setup_complex_at140020(self):
        duration = TestDateHeaders(self, mopidy_waitforinternet.WaitForInternetExtension())
        self.assertGreaterEqual(duration, 0)
        self.assertLess(duration, 0.4)

    @freeze_time('2022-07-01 18:18:20', ignore=['tests'])
    def test_waitforinternet_setup_complex_at181820(self):
        duration = TestDateHeaders(self, mopidy_waitforinternet.WaitForInternetExtension())
        self.assertGreaterEqual(duration, 0)
        self.assertLess(duration, 0.4)

    @freeze_time('2022-07-01 14:00:20', ignore=['tests'])
    def test_waitfortimesync_setup_complex_at140020(self):
        duration = TestDateHeaders(self, mopidy_waitfortimesync.WaitForTimeSyncExtension())
        self.assertGreaterEqual(duration, 0)
        self.assertLess(duration, 0.4)

    @freeze_time('2022-07-01 14:00:35', ignore=['tests'])
    def test_waitfortimesync_setup_complex_at140035(self):
        duration = TestDateHeaders(self, mopidy_waitfortimesync.WaitForTimeSyncExtension())
        self.assertGreaterEqual(duration, 1)
        self.assertLess(duration, 1.4)

    @freeze_time('2022-07-01 14:00:59', ignore=['tests'])
    def test_waitfortimesync_setup_complex_at140059(self):
        duration = TestDateHeaders(self, mopidy_waitfortimesync.WaitForTimeSyncExtension())
        self.assertGreaterEqual(duration, 3)
        self.assertLess(duration, 3.4)

    def tearDown(self):
        mopidy_waitforinternet.check_urls = self.backup_check_urls
