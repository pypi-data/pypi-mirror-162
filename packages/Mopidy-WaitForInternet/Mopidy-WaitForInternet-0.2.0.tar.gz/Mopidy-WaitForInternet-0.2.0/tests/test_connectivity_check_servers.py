import time
import unittest
from datetime import datetime

import pytest

import requests

import mopidy_waitforinternet


class ConnectivityCheckServersTest(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_servers(self):
        self.assertGreater(len(mopidy_waitforinternet.check_urls), 2)

        t_start = time.monotonic()
        for url in mopidy_waitforinternet.check_urls:
            resp = requests.get(url, timeout=2, allow_redirects=False)
            self.assertEqual(resp.status_code, 200)
            self.assertLess(abs((datetime.utcnow() - datetime.strptime(resp.headers['Date'], '%a, %d %b %Y %H:%M:%S GMT')).total_seconds()), 5)
        t_stop = time.monotonic()

        self.assertLess(t_stop - t_start, len(mopidy_waitforinternet.check_urls))
        with self.capsys.disabled():
            print()
            print(f'CONNECTIVITY CHECK SERVER TEST: Tested {len(mopidy_waitforinternet.check_urls):d} servers in {t_stop - t_start:.3f} seconds.')
