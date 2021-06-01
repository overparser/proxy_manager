import json
import time


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

    @staticmethod
    def dict(self):
        return {'login': self.login, 'password': self.password, 'ip': self.ip, 'port': self.port}


class Proxy:
    def __init__(self, ip=None, port=None, login=None, password=None, proxy_interval=2, proxy_error_interval=8,
                 can_sleep=True):
        """

        :param proxy: {login:str, password:str, ip:str, port:str}
        :param formatter_name:
            http_requests - {'http': login:pass@ip:port},
            https_requests - {'https': login:pass@ip:port},
            aiohttp - "http://login:password@ip:port"
        :param proxy_interval:
        """
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password
        self.last_time = 0
        self.formatters = Formatters()
        self.formatter = None
        self.proxy_interval = proxy_interval
        self.proxy_error_interval = proxy_error_interval
        self.can_sleep = can_sleep

    def from_dict(self, dict_):
        self.__dict__.update(dict_)
        return self

    def set_formatter(self, formatter_name):
        self.formatter = getattr(Formatters, formatter_name)

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
        if not self.formatter:
            raise AttributeError('formatter does not exist')

        return self.formatter(self)

    def __enter__(self):
        self._maybe_sleep()
        return self._formated_proxy()

    def __exit__(self, type, value, traceback):
        if isinstance(value, Exception):
            self.last_time += 8

def read_lines(path):
    # TODO добавить валидацию os.path для вложенных директорий
    with open(path, "r") as file:
        reader = file.read()
    return [row for row in reader.split("\n") if row]


class RowParser:
    def __init__(self, parse_pattern='ip:port:login:password'):
        """
            :param parse_pattern: 'ip:port@login:password' с любыми разделителями, сохраняется указанный порядок значений
        """
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

class ProxyLoader:
    @staticmethod
    def load_from_txt(path, parse_pattern=None):
        rows = read_lines(path)
        proxies: list[dict] = RowParser(parse_pattern).parse_each_row(rows)
        return [Proxy().from_dict(dict_proxy) for dict_proxy in proxies]

    def from_rows(self, rows, parse_pattern):
        proxies: list[dict] = RowParser(parse_pattern).parse_each_row(rows)
        return [Proxy().from_dict(dict_proxy) for dict_proxy in proxies]

    @staticmethod
    def load_from_csv(path):
        pass

class ProxyPool:
    def __init__(self, proxy_interval=None, proxy_error_interval=None,
                          can_sleep=None):
        """
        :param proxies: [Proxy, ...]
        """
        self.proxy_interval = proxy_interval
        self.proxy_error_interval = proxy_error_interval
        self.can_sleep = can_sleep
        self.proxies = []

    def get(self, formatter_name):
        """
        :param formatter_name:
            http_requests - {'http': login:pass@ip:port},
            https_requests - {'https': login:pass@ip:port},
            aiohttp - "http://login:password@ip:port"

        :return: Proxy
        """
        # можно оптимизировать под bisect
        self.proxies.sort(key=lambda obj: obj.last_time)
        proxy = self.proxies[0]
        proxy.set_formatter(formatter_name)
        return proxy

    def _set_proxy_setting(self, proxy):
        proxy.proxy_interval = self.proxy_interval
        proxy.proxy_error_interval = self.proxy_interval
        proxy.can_sleep = self.can_sleep

    def add_proxy(self, proxy):
        self._set_proxy_setting(proxy)
        self.proxies.append(proxy)

    def add_proxies(self, proxies):
        [self.add_proxy(proxy) for proxy in proxies]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class ProxyManager:
    def __init__(self, proxy_interval=2, proxy_error_interval=8, can_sleep=True):
        self.proxy_pool = ProxyPool(proxy_interval=proxy_interval, proxy_error_interval=proxy_error_interval,
                                    can_sleep=can_sleep)
        self.proxy_loader = ProxyLoader()

    def load_from_txt(self, path, parse_pattern='login:password@ip:port:'):
        proxies = self.proxy_loader.load_from_txt(path, parse_pattern)
        self.proxy_pool.add_proxies(proxies)

    def from_rows(self, rows: list[dict], parse_pattern='login:password@ip:port:'):
        proxies = self.proxy_loader.from_rows(rows, parse_pattern)
        self.proxy_pool.add_proxies(proxies)

    def get(self, formatter_name):
        return self.proxy_pool.get(formatter_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

if __name__ == "__main__":
    pm = ProxyManager()
    pm.load_from_txt('proxies.txt', 'ip:port:login:password')
    for i in range(155):
        with pm.get('aiohttp') as proxy:
            print(proxy)
