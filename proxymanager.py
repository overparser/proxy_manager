import json
from bisect import bisect
import time

def reade_lines(path):
    with open(path, "r") as file:
        reader = file.read()
    return [row for row in reader.split("\n") if row]

class Formatters:
    @staticmethod
    def string_proxy(self):
        return f"http://{self.login}:{self.password}@{self.ip}:{self.port}"

    @staticmethod
    def http_dict_proxy(self):
        return {
            'http': f"http://{self.login}:{self.password}@{self.ip}:{self.port}"
        }

    @staticmethod
    def https_dict_proxy(self):
        return {
            'https': f"http://{self.login}:{self.password}@{self.ip}:{self.port}"
        }



class Proxy:
    def __init__(self, ip=None, port=None, login=None, password=None, get_proxy_interval=2, formatter='string_proxy'):
        self.ip = ip
        self.port = port
        self.login = login
        self.password = password
        self.last_time = 0
        self.formatter = Formatters.__dict__[formatter]
        self.get_proxy_interval = get_proxy_interval

    def maybe_sleep(self):
        if self.last_time > time.time():
            self.increase_last_time()
            print("sleep")
            time.sleep(time.time() - self.last_time)
            return

        self.increase_last_time()

    def from_row(self, row):
        self.ip, self.port, self.login, self.password = row.split(":")
        return self

    def increase_last_time(self):
        self.last_time = time.time() + self.get_proxy_interval

    def formated_proxy(self):
        return self.formatter(self)

    def __enter__(self):
        self.maybe_sleep()
        return self.formated_proxy()

    def __exit__(self, type, value, traceback):
        if isinstance(value, NameError):
            self.last_time += 8

    def __repr__(self):
        return json.dumps(self.__dict__, indent=4)


class ProxyManager:
    def __init__(self, proxies=None, formatter='string_proxy'):
        self.loader = reade_lines
        self.formatter = formatter
        self.proxies = []

    def get(self):
        self.proxies.sort(key=lambda obj: obj.last_time)
        return self.proxies[0]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def load(self, path):
        proxy_list = self.loader(path)
        self.proxies = [Proxy().from_row(row) for row in proxy_list]


if __name__ == "__main__":
    proxy_manager = ProxyManager()
    proxy_manager.load("proxies.txt")
    for i in range(15):
        with proxy_manager.get() as proxy:
            print(proxy)

    # with proxy_manager.get() as proxy:
    #     print(proxy)
    # with proxy_manager as proxy:
    #     with proxy as proxy:
    #         print(proxy)
