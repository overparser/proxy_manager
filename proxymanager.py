import time
import asyncio
import requests


def base_formatter(self):
    pass


class Formatters:
    @staticmethod
    def aiohttp(self):
        if self.login:
            return f"http://{self.login}:{self.password}@{self.ip}:{self.port}"
        return f"http://{self.ip}:{self.port}"

    @staticmethod
    def http_requests(self):
        if self.login:
            return {
                "http": f"http://{self.login}:{self.password}@{self.ip}:{self.port}"
            }
        return {"http": f"http://{self.ip}:{self.port}"}

    @staticmethod
    def https_requests(self):
        if self.login:
            return {
                "https": f"https://{self.login}:{self.password}@{self.ip}:{self.port}"
            }
        return {"https": f"https://{self.ip}:{self.port}"}

    @staticmethod
    def dict(self):
        if self.login:
            return {
                "login": self.login,
                "password": self.password,
                "ip": self.ip,
                "port": self.port,
            }
        return {"ip": self.ip, "port": self.port}


def read_lines(path):
    with open(path, "r") as file:
        reader = file.read()
    return [row for row in reader.split("\n") if row]


class RowParser:
    def __init__(self, parse_pattern="ip:port:login:password"):
        """
        :param parse_pattern: 'ip:port@login:password' с любыми разделителями, сохраняется указанный порядок значений
        """
        self.parse_pattern = parse_pattern
        self.delimiters = None
        self.key_positions = None

    def _get_delimiters(self):
        if not self.delimiters:
            self.delimiters = self._parse_items(
                self.parse_pattern, ["login", "password", "ip", "port"]
            )

    def _get_key_positions(self):
        if not self.key_positions:
            self.key_positions = self._parse_items(self.parse_pattern, self.delimiters)

    def _parse_items(self, row, delimiters):
        for delim in delimiters:
            row = row.replace(delim, "!#$%")
        return [i for i in row.split("!#$%") if i]

    def _check_errors(self, row):
        for delim in self.delimiters:
            if self.delimiters.count(delim) < row.count(delim):
                raise AttributeError("Delimiter exists in row field")

    def parse_row(self, row):
        self._get_delimiters()
        self._check_errors(row)
        self._get_key_positions()
        proxy_items = self._parse_items(row, self.delimiters)
        return dict(zip(self.key_positions, proxy_items))

    def parse_each_row(self, rows):
        return [self.parse_row(row) for row in rows]


class ProxyLoader:
    @staticmethod
    def load_from_txt(path, parse_pattern=None):
        """
        Загрузка из плоского файла где каждая прокси начинается с новой строки
        :param path:
        :param parse_pattern:
        :return: [dict, ...]
        """

        rows = read_lines(path)
        return RowParser(parse_pattern).parse_each_row(rows)

    def from_rows(self, rows, parse_pattern):
        """
        Парсит прокси из списка строк прокси
        :param rows: [str, str, ...]
        :param parse_pattern: 'login:passwor@ip:port'
        :return: [dict, dict, ...]
        """
        return RowParser(parse_pattern).parse_each_row(rows)


class Proxy:
    def __init__(
        self,
        ip=None,
        port=None,
        login=None,
        password=None,
        proxy_interval=2,
        proxy_error_interval=8,
        can_sleep=True,
        formatter=None,
    ):
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
        self.proxy_interval = proxy_interval
        self.proxy_error_interval = proxy_error_interval
        self.can_sleep = can_sleep
        self.formatter = formatter

    def set_formatter(self, formatter):
        self.formatter = formatter

    def get(self):
        return self.formatter(self)

    def from_dict(self, dict_):
        self.__dict__.update(dict_)
        return self

    def _increase_last_time(self):
        self.last_time = time.time() + self.proxy_interval

    def _maybe_sleep(self):
        if self.can_sleep and self.last_time > time.time():
            print("sleep")
            time.sleep(self.last_time - time.time())
            return

    async def _maybe_asleep(self):
        if self.can_sleep and self.last_time > time.time():
            print("asleep")
            await asyncio.sleep(self.last_time - time.time())
            return

    def __enter__(self):
        self._maybe_sleep()
        self._increase_last_time()
        return self.formatter(self)

    def __exit__(self, type, value, traceback):
        """При возникновении ошибки увеличивает интервал для прокси"""
        if isinstance(value, Exception):
            self.last_time += self.proxy_error_interval

    async def __aenter__(self):
        await self._maybe_asleep()
        self._increase_last_time()
        return self.formatter(self)

    async def __aexit__(self, type, value, traceback):
        if isinstance(value, Exception):
            self.last_time += self.proxy_error_interval


class ProxyPool:
    def __init__(
        self, formatter, proxy_interval=None, proxy_error_interval=None, can_sleep=None
    ):
        """
        :param proxies: [Proxy, ...]
        """
        self.proxy_interval = proxy_interval
        self.proxy_error_interval = proxy_error_interval
        self.can_sleep = can_sleep
        self.formatter = formatter
        self.proxies = []

    def get(self):
        """
        :return: Proxy
        """
        # можно оптимизировать под bisect
        self.proxies.sort(key=lambda obj: obj.last_time)
        proxy = self.proxies[0]
        return proxy

    def set_formatter(self, formatter):
        self.formatter = formatter
        for proxy in self.proxies:
            proxy.set_formatter(formatter)

    def add_proxy_from_dict(self, proxy_dict):
        proxy = Proxy(
            proxy_interval=self.proxy_interval,
            proxy_error_interval=self.proxy_error_interval,
            can_sleep=self.can_sleep,
            formatter=self.formatter,
        )
        proxy.from_dict(proxy_dict)
        self.proxies.append(proxy)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class ProxyManager:
    def __init__(
        self,
        proxy_interval=2,
        proxy_error_interval=8,
        can_sleep=True,
        formatter_name="dict",
    ):
        """
        Загружает прокси из указанного источника, должен работать через контекст менеджер,
         контролирует частоту использования прокси, при возникновении ошибки увеличивает
         задержку времени на использование прокси.


        :param proxy_interval: добавляет указанный интервал в секундах к текущему времени каждый раз когда используется прокси
        :param proxy_error_interval: добавляет указанный интервал на прокси в случае ошибки
        :param can_sleep: bool, если время прокси больше чем текущее время то использует time.sleep/asyncio.sleep
        :param formatter_name: имя форматтера прокси - 'dict', 'aiohttp', 'http_requests', 'https_requests'
        пока время прокси не станет меньше текущего времени
        """
        self.formatter = getattr(Formatters, formatter_name)
        self.proxy_pool = ProxyPool(
            formatter=self.formatter,
            proxy_interval=proxy_interval,
            proxy_error_interval=proxy_error_interval,
            can_sleep=can_sleep,
        )
        self.proxy_loader = ProxyLoader()

    def set_formatter(self, formatter_name: str):
        self.formatter = getattr(Formatters, formatter_name)
        self.proxy_pool.set_formatter(self.formatter)

    def set_custom_formatter(self, formatter):
        self.formatter = formatter
        self.proxy_pool.set_formatter(self.formatter)

    def __len__(self):
        return len(self.proxy_pool.proxies)

    def __iter__(self):
        return (proxy.get() for proxy in self.proxy_pool.proxies)

    def load_from_txt(self, path, parse_pattern):
        """
        :param path: путь к файлу прокси
        :param parse_pattern указывается порядок полей прокси и их разделители:
        'login:password@ip:port' или 'ip:port',
        разделители не должны встречаться в полях строки прокси иначе будет AttributeError
        :return: None
        """
        proxies: list[dict] = self.proxy_loader.load_from_txt(path, parse_pattern)
        [self.proxy_pool.add_proxy_from_dict(proxy_dict) for proxy_dict in proxies]

    def from_rows(self, rows: list[str], parse_pattern):
        """
        :param rows: [str, str, str]
        :param parse_pattern: 'login:password@ip:port' или 'ip:port'
         могут исользоваться любые разделители кроме символов встречающихся в логине/пароле
        :return: None
        """
        proxies: list[dict] = self.proxy_loader.from_rows(rows, parse_pattern)
        [self.proxy_pool.add_proxy_from_dict(proxy_dict) for proxy_dict in proxies]

    def get(self):
        return self.proxy_pool.get()

    def __enter__(self):
        return self.get()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def custom_formatter(self):
    return [self.ip, self.port, self.login, self.password]


if __name__ == "__main__":
    pm = ProxyManager()
    rows = [
        '45.87.249.8:7586@tuthixen:some_password',
        '45.87.249.44:7622@tuthixen:some_password',
        '45.87.249.84:7662@tuthixen:some_password'
    ]
    pm.from_rows(rows, "ip:port@login:password")
    pm.set_formatter('dict')
    for _ in pm:
        with pm.get() as proxy:
            print(proxy)

    print('switching formatter')
    pm.set_formatter('aiohttp')
    for _ in pm:
        with pm.get() as proxy:
            print(proxy)

    # for i in range(10):
    #     with pm.get() as proxy:
    #         print(proxy)
    #
    # pm.set_formatter("aiohttp")
    #
    # for i in range(10):
    #     with pm.get() as proxy:
    #         print(proxy)
    #
    # pm.set_formatter("http_requests")
    # for i in range(10):
    #     with pm.get() as proxy:
    #         print(proxy)
    #
    # pm.set_custom_formatter(custom_formatter)
    # for i in range(10):
    #     with pm.get() as proxy:
    #         print(proxy)
