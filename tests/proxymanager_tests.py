import unittest
from proxymanager import ProxyManager, RowParser
import asyncio
import requests

class TestProxyManagerContext(unittest.TestCase):
    context_manager_result = [
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

    def test_sync_context(self):
        pm = ProxyManager()
        pm.load_from_txt("test_proxies.txt", "login:password@ip:port")
        proxies = []
        for i in range(10):
            with pm.get("aiohttp") as proxy:
                proxies.append(proxy)
        self.assertEqual(proxies, self.context_manager_result)

    def test_async_context(self):
        context_proxies = asyncio.run(self._async_context())
        self.assertEqual(context_proxies, self.context_manager_result)


    async def _async_context(self):
        pm = ProxyManager()
        pm.load_from_txt("test_proxies.txt", "login:password@ip:port")
        proxies = []
        for i in range(10):
            async with pm.get("aiohttp") as proxy:
                proxies.append(proxy)
        return proxies

class TestRowParser(unittest.TestCase):
    def test_a(self):
        row = '45.87.249.8:7586@some_login:some_password'
        pattern = 'ip:port@login:password'
        r = RowParser(pattern)
        result = r.parse_row(row)
        self.assertEqual({'ip': '45.87.249.8', 'port': '7586', 'login':'some_login', 'password': 'some_password'}, result)

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
