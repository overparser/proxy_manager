import time
import asyncio
import requests

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
                'http': f"http://{self.login}:{self.password}@{self.ip}:{self.port}"
            }
        return {
            'http': f"http://{self.ip}:{self.port}"
        }

    @staticmethod
    def https_requests(self):
        if self.login:
            return {
                'https': f"https://{self.login}:{self.password}@{self.ip}:{self.port}"
            }
        return {
            'https': f"https://{self.ip}:{self.port}"
        }

    @staticmethod
    def dict(self):
        if self.login:
            return {'login': self.login, 'password': self.password, 'ip': self.ip, 'port': self.port}
        return {'ip': self.ip, 'port': self.port}


def read_lines(path):
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

    def _check_errors(self, row):
        for delim in self.delimiters:
            if self.delimiters.count(delim) < row.count(delim):
                raise AttributeError('Delimiter exists in row field')

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

    def _set_formatter(self, formatter_name):
        """Устанвливает формат прокси и обработку исключений
        formatter_name: 'dict', 'aiohttp', 'http_requests', 'https_requests'
        """
        self.formatter = getattr(self.formatters, formatter_name)

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

    def _formated_proxy(self):
        if not self.formatter:
            raise AttributeError('formatter does not exist')

        return self.formatter(self)

    def __enter__(self):
        self._maybe_sleep()
        self._increase_last_time()
        return self._formated_proxy()

    def __exit__(self, type, value, traceback):
        if isinstance(value, Exception):
            self.last_time += self.proxy_error_interval

    async def __aenter__(self):
        await self._maybe_asleep()
        self._increase_last_time()
        return self._formated_proxy()

    async def __aexit__(self, type, value, traceback):
        if isinstance(value, Exception):
            self.last_time += self.proxy_error_interval


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
        proxy._set_formatter(formatter_name)
        return proxy

    def add_proxy_from_dict(self, proxy_dict):
        proxy = Proxy(proxy_interval=self.proxy_interval, proxy_error_interval=self.proxy_error_interval, can_sleep=self.can_sleep)
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
    # TODO добавить хандлеры ошибок под типы форматтеров
    def __init__(self, proxy_interval=2, proxy_error_interval=8, can_sleep=True):
        """
        Загружает прокси из указанного источника, должен работать через контекст менеджер,
         контролирует частоту использования прокси, при возникновении ошибки увеличивает
         задержку времени на использование прокси.

        
        :param proxy_interval: добавляет указанный интервал в секундах каждый раз когда используется прокси
        :param proxy_error_interval: добавляет указанный интервал на прокси в случае ошибки
        :param can_sleep: bool, если время прокси больше чем текущее время то использует time.sleep/asyncio.sleep
        пока время прокси не станет меньше текущего времени
        """
        self.proxy_pool = ProxyPool(proxy_interval=proxy_interval, proxy_error_interval=proxy_error_interval,
                                    can_sleep=can_sleep)
        self.proxy_loader = ProxyLoader()

    def load_from_txt(self, path, parse_pattern='login:password@ip:port'):
        """

        :param path: путь к файлу прокси
        :param parse_pattern указывается порядок полей прокси и их разделители:
        'login:password@ip:port' или 'ip:port',
        разделители не должны встречаться в полях строки прокси иначе будет AttributeError
        :return: None
        """
        proxies: list[dict] = self.proxy_loader.load_from_txt(path, parse_pattern)
        [self.proxy_pool.add_proxy_from_dict(proxy_dict) for proxy_dict in proxies]

    def from_rows(self, rows: list[dict], parse_pattern='login:password@ip:port'):
        """

        :param rows: [str, str, str]
        :param parse_pattern: 'login:password@ip:port' или 'ip:port'
         могут исользоваться любые разделители кроме символов встречающихся в логине/пароле
        :return: None
        """
        proxies: list[dict] = self.proxy_loader.from_rows(rows, parse_pattern)
        [self.proxy_pool.add_proxy_from_dict(proxy_dict) for proxy_dict in proxies]

    def get(self, formatter_name):
        return self.proxy_pool.get(formatter_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass