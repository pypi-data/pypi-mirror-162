import socket
import time
import unittest

import mock

import mopidy_waitforinternet


class WaitForInternetExtensionTest(unittest.TestCase):

    def setUp(self):
        self.backup_check_urls = mopidy_waitforinternet.check_urls

    def test01_get_default_config(self):
        ext = mopidy_waitforinternet.WaitForInternetExtension()

        config = ext.get_default_config()

        self.assertIn('[waitforinternet]', config)
        self.assertIn('enabled = true', config)

    def test02_setup_realrun(self):  # DO NOT MODIFY mopidy_waitforinternet.check_urls before this test!
        registry = mock.Mock()

        ext = mopidy_waitforinternet.WaitForInternetExtension()

        t_start = time.monotonic()
        ext.setup(registry)
        t_stop = time.monotonic()

        registry.add.assert_not_called()
        self.assertGreater(t_stop - t_start, 0)
        self.assertLess(t_stop - t_start, 0.999)

    def test03_setup_transient_nameresolutionfailure(self):
        for name in [
            'nosuchhost.nosuchdomain1.arpa',
            'nosuchhost.nosuchdomain2.arpa',
            'nosuchhost.nosuchdomain3.arpa',
            'nosuchhost.nosuchdomain4.arpa',
            'nosuchhost.nosuchdomain5.arpa'
        ]:
            try:
                socket.gethostbyname(name)
            except Exception:
                pass

        registry = mock.Mock()

        mopidy_waitforinternet.check_urls = [
            'https://nosuchhost.nosuchdomain1.arpa/name-resolution-failure',
            'https://nosuchhost.nosuchdomain2.arpa/name-resolution-failure',
            'https://nosuchhost.nosuchdomain3.arpa/name-resolution-failure',
            'https://nosuchhost.nosuchdomain4.arpa/name-resolution-failure',
            'https://nosuchhost.nosuchdomain5.arpa/name-resolution-failure',
            'https://cloudflare-dns.com/dns-query?dns=AAABAAABAAAAAAAACmNsb3VkZmxhcmUDY29tAAABAAE',
            'https://dns.google/dns-query?dns=AAABAAABAAAAAAAABmdvb2dsZQNjb20AAAEAAQ'
        ]

        ext = mopidy_waitforinternet.WaitForInternetExtension()

        t_start = time.monotonic()
        ext.setup(registry)
        t_stop = time.monotonic()

        registry.add.assert_not_called()
        self.assertGreater(t_stop - t_start, 5)
        self.assertLess(t_stop - t_start, 7)

    def test03_setup_transient_tcpconnectionfailure(self):
        registry = mock.Mock()

        mopidy_waitforinternet.check_urls = [
            'https://127.182.103.41/tcp-connection-failure',
            'https://127.182.103.42/tcp-connection-failure',
            'https://127.182.103.43/tcp-connection-failure',
            'https://127.182.103.44/tcp-connection-failure',
            'https://127.182.103.45/tcp-connection-failure',
            'https://cloudflare-dns.com/dns-query?dns=AAABAAABAAAAAAAACmNsb3VkZmxhcmUDY29tAAABAAE',
            'https://dns.google/dns-query?dns=AAABAAABAAAAAAAABmdvb2dsZQNjb20AAAEAAQ'
        ]

        ext = mopidy_waitforinternet.WaitForInternetExtension()

        t_start = time.monotonic()
        ext.setup(registry)
        t_stop = time.monotonic()

        registry.add.assert_not_called()
        self.assertGreater(t_stop - t_start, 5)
        self.assertLess(t_stop - t_start, 7)

    def test04_setup_permanent_nameresolutionfailure(self):
        registry = mock.Mock()

        mopidy_waitforinternet.check_urls = [
            'https://nosuchhost.nosuchdomain1.arpa/name-resolution-failure',
            'https://nosuchhost.nosuchdomain2.arpa/name-resolution-failure',
            'https://nosuchhost.nosuchdomain3.arpa/name-resolution-failure',
            'https://nosuchhost.nosuchdomain4.arpa/name-resolution-failure',
            'https://nosuchhost.nosuchdomain5.arpa/name-resolution-failure'
        ]

        ext = mopidy_waitforinternet.WaitForInternetExtension()

        t_start = time.monotonic()
        ext.setup(registry)
        t_stop = time.monotonic()

        registry.add.assert_not_called()
        self.assertGreaterEqual(t_stop - t_start, 300)
        self.assertLess(t_stop - t_start, 305)

    def tearDown(self):
        mopidy_waitforinternet.check_urls = self.backup_check_urls
