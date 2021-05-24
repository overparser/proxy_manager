import json
from bisect import bisect
import time

def reade_lines(path):
    with open(path, "r") as file:
        reader = file.read()
    return [row for row in reader.split("\n") if row]

class Formatters:
    @staticmethod
    def aiohttp(self):
        return f"http://{self.login}:{self.password}@{self.ip}:{self.port}"

    @staticmethod
    def http_requests(self):
        return {
            'http': f"http://{self.login}:{self.password}@{self.ip}:{self.port}"
        }

    @staticmethod
    def https_requests(self):
        return {
            'https': f"http://{self.login}:{self.password}@{self.ip}:{self.port}"
        }



class Proxy:
    def __init__(self, proxy: dict, formatter_name=None, proxy_interval=2, proxy_error_interval=8,
                 can_sleep=True):
        """

        :param proxy: {login:str, password:str, ip:str, port:str}
        :param formatter_name:
            http_requests - {'http': login:pass@ip:port},
            https_requests - {'https': login:pass@ip:port},
            aiohttp - "http://login:password@ip:port"
        :param proxy_interval:
        """
        self.__dict__.update(proxy)
        self.last_time = 0
        self.formatter = getattr(Formatters, formatter_name)
        self.proxy_interval = proxy_interval
        self.proxy_error_interval = proxy_error_interval
        self.can_sleep = can_sleep

    def _increase_last_time(self):
        self.last_time = time.time() + self.proxy_interval

    def _maybe_sleep(self):
        if self.can_sleep and self.last_time > time.time():
            print("sleep")
            time.sleep(self.last_time - time.time())
            self._increase_last_time()
            return
        self._increase_last_time()

    def _formated_proxy(self):
        return self.formatter(self)

    def __enter__(self):
        self._maybe_sleep()
        return self._formated_proxy()

    def __exit__(self, type, value, traceback):
        if isinstance(value, NameError):
            self.last_time += 8

    def __repr__(self):
        return json.dumps({
            self.ip: '45.87.249.8', self.port: '7586', self.login: 'tuthixen-dest',
            self.password: '53d8tl329rrx', self.last_time: 0, self.proxy_interval: 2,
            self.proxy_error_interval: 8, self.can_sleep: True}, indent=4)


class Proxies:
    def __init__(self, proxies=None):
        self.proxies = proxies or []

    def get(self):
        # можно оптимизировать под bisect
        self.proxies.sort(key=lambda obj: obj.last_time)
        return self.proxies[0]

    def add_proxy(self, proxy: Proxy):
        self.proxies.append(proxy)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class ProxyManager:
    def __init__(self, path=None, parse_pattern='ip:port:login:password', formatter_name='aiohttp', proxy_interval=2,
                 can_sleep=True):
        self.proxy_loader = ProxyLoader()
        self.proxy_parser = ProxyParser(parse_pattern)
        self.proxy = Proxy
        self.proxies = Proxies()
        self.path = path
        self.parse_pattern = parse_pattern
        self.formatter_name = formatter_name
        self.proxy_interval = proxy_interval
        self.can_sleep = can_sleep

    def load(self):
        proxy_dicts = self.proxy_loader.load_from_txt(self.path, self.parse_pattern)

        for proxy_dict in proxy_dicts:
            proxy = Proxy(proxy_dict, formatter_name=self.formatter_name, proxy_interval=2, proxy_error_interval=8, can_sleep=self.can_sleep)
            self.proxies.add_proxy(proxy)
        return self.proxies

class ProxyLoader:
    @staticmethod
    def load_from_txt(path, parse_pattern='ip:port:login:password'):
        proxy_rows = reade_lines(path)
        proxy_dicts = ProxyParser(parse_pattern).parse_each_row(proxy_rows)
        return proxy_dicts

    @staticmethod
    def load_from_json(path):
        pass

    @staticmethod
    def load_from_csv(path):
        pass

class ProxyParser:
    def __init__(self, parse_pattern='ip:port:login:password'):
        self.parse_pattern = parse_pattern
        self.delimiters = None
        self.key_positions = None

    def _get_delimiters(self):
        if not self.delimiters:
            self.delimiters = self._parse_items(self.parse_pattern, ['login', 'password', 'ip', 'port'])

    def _get_key_positions(self):
        if not self.key_positions:
            self.key_positions = self._parse_items(self.parse_pattern, self.delimiters)

    def _parse_items(self, row, delimiters):
        for delim in delimiters:
            row = row.replace(delim, '!#$%')
        return [i for i in row.split('!#$%') if i]

    def parse_row(self, row):
        self._get_delimiters()
        self._get_key_positions()
        proxy_items = self._parse_items(row, self.delimiters)
        return dict(zip(self.key_positions, proxy_items))

    def parse_each_row(self, rows):
        return [self.parse_row(row) for row in rows]

if __name__ == "__main__":
    pm = ProxyManager('proxies.txt').load()
    for i in range(155):
        with pm.get() as proxy:
            print(proxy)

    # with proxy_manager.get() as proxy:
    #     print(proxy)
    # with proxy_manager as proxy:
    #     with proxy as proxy:
    #         print(proxy)
