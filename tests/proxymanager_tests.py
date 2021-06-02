import unittest
from proxymanager import ProxyManager, RowParser
import asyncio
import requests


class TestProxyManagerContext(unittest.TestCase):
    aiohttp_result = [
        "http://45.87.249.8:7586@some_login:some_password",
        "http://45.87.249.44:7622@some_login:some_password",
        "http://45.87.249.84:7662@some_login:some_password",
        "http://45.87.249.134:7712@some_login:some_password",
        "http://45.87.249.80:7658@some_login:some_password",
        "http://45.87.249.88:7666@some_login:some_password",
        "http://45.87.249.173:7751@some_login:some_password",
        "http://45.87.249.85:7663@some_login:some_password",
        "http://45.87.249.112:7690@some_login:some_password",
        "http://45.87.249.254:7832@some_login:some_password",
    ]
    dict_result = [
        {
            "login": "45.87.249.8",
            "password": "7586",
            "ip": "some_login",
            "port": "some_password",
        },
        {
            "login": "45.87.249.44",
            "password": "7622",
            "ip": "some_login",
            "port": "some_password",
        },
        {
            "login": "45.87.249.84",
            "password": "7662",
            "ip": "some_login",
            "port": "some_password",
        },
        {
            "login": "45.87.249.134",
            "password": "7712",
            "ip": "some_login",
            "port": "some_password",
        },
        {
            "login": "45.87.249.80",
            "password": "7658",
            "ip": "some_login",
            "port": "some_password",
        },
        {
            "login": "45.87.249.88",
            "password": "7666",
            "ip": "some_login",
            "port": "some_password",
        },
        {
            "login": "45.87.249.173",
            "password": "7751",
            "ip": "some_login",
            "port": "some_password",
        },
        {
            "login": "45.87.249.85",
            "password": "7663",
            "ip": "some_login",
            "port": "some_password",
        },
        {
            "login": "45.87.249.112",
            "password": "7690",
            "ip": "some_login",
            "port": "some_password",
        },
        {
            "login": "45.87.249.254",
            "password": "7832",
            "ip": "some_login",
            "port": "some_password",
        },
    ]
    http_requests_result = [
        {"http": "http://45.87.249.8:7586@some_login:some_password"},
        {"http": "http://45.87.249.44:7622@some_login:some_password"},
        {"http": "http://45.87.249.84:7662@some_login:some_password"},
        {"http": "http://45.87.249.134:7712@some_login:some_password"},
        {"http": "http://45.87.249.80:7658@some_login:some_password"},
        {"http": "http://45.87.249.88:7666@some_login:some_password"},
        {"http": "http://45.87.249.173:7751@some_login:some_password"},
        {"http": "http://45.87.249.85:7663@some_login:some_password"},
        {"http": "http://45.87.249.112:7690@some_login:some_password"},
        {"http": "http://45.87.249.254:7832@some_login:some_password"},
    ]

    def _sync_context(self, formatter_name):
        pm = ProxyManager(formatter_name=formatter_name)
        pm.load_from_txt("test_proxies.txt", "login:password@ip:port")
        proxies = []
        for i in range(10):
            with pm.get() as proxy:
                proxies.append(proxy)
        return proxies

    def test_aiohttp_sync_context(self):
        proxies = self._sync_context("aiohttp")
        self.assertEqual(proxies, self.aiohttp_result)

    def test_dict_sync_context(self):
        proxies = self._sync_context("dict")
        self.assertEqual(proxies, self.dict_result)

    def test_http_requests_sync_context(self):
        proxies = self._sync_context("http_requests")
        self.assertEqual(proxies, self.http_requests_result)

    def test_dict_async_context(self):
        context_proxies = asyncio.run(self._async_context("dict"))
        self.assertEqual(context_proxies, self.dict_result)

    def test_http_requests_async_context(self):
        context_proxies = asyncio.run(self._async_context("http_requests"))
        self.assertEqual(context_proxies, self.http_requests_result)

    def test_aiohttp_async_context(self):
        context_proxies = asyncio.run(self._async_context("aiohttp"))
        self.assertEqual(context_proxies, self.aiohttp_result)

    async def _async_context(self, formatter_name):
        pm = ProxyManager(formatter_name=formatter_name)
        pm.load_from_txt("test_proxies.txt", "login:password@ip:port")
        proxies = []
        for i in range(10):
            async with pm.get() as proxy:
                proxies.append(proxy)
        return proxies


class TestRowParser(unittest.TestCase):
    def test_a(self):
        row = '45.87.249.8:7586@some_login:some_password'
        pattern = 'ip:port@login:password'
        r = RowParser(pattern)
        result = r.parse_row(row)
        self.assertEqual({'ip': '45.87.249.8', 'port': '7586', 'login': 'some_login', 'password': 'some_password'}, result)

    def test_b(self):
        row = '45.87.249.8:7586@s@me_l@gin:some_password'
        pattern = 'ip:port@login:password'
        r = RowParser(pattern)
        with self.assertRaises(AttributeError):
            r.parse_row(row)

    def test_c(self):
        row = '45.87.249.8:!%7586@some_login$$:some_password'
        pattern = 'ip:!%port@login$$:password'
        r = RowParser(pattern)
        result = r.parse_row(row)
        self.assertEqual({'ip': '45.87.249.8', 'port': '7586', 'login': 'some_login', 'password': 'some_password'},
                         result)


if __name__ == "__main__":
    unittest.main()
