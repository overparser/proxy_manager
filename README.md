# ProxyManager
Создан в результате необходимости удобного контроля интервалов прокси.
В случае возникновения ошибки в области контекст менеджера автоматически увеличивает интервал прокси.
Прокси считается свободной если последнее время ее использования не превышает текущее время. 
Если свободных прокси нет то использует asyncio.sleep/time.sleep в зависимости от контекст менеджера,
пока время прокси не станет меньше чем текущее время.
```
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
            пока время прокси не станет меньше текущего времени. Можно отключить тогда будет использоваться просто как
            сортировка ошибочных прокси

        :param formatter_name: имя форматтера прокси - 'dict', 'aiohttp', 'http_requests', 'https_requests'
        """
```



## Context_manager
```
pm = ProxyManager()
pm.load_from_txt('proxies.txt', parse_pattern='login:password@ip:port')

for i in range(15):
    with pm.get('http_requests') as proxy:
        print(proxy)
```

#### Output:
```
{'http': 'http://tuthixen:some_password@45.87.249.8:7586'}
{'http': 'http://tuthixen:some_password@45.87.249.44:7622'}
sleep
{'http': 'http://tuthixen:some_password@45.87.249.8:7586'}
{'http': 'http://tuthixen:some_password@45.87.249.44:7622'}
...
```

### Async context_manager
```
async def loop_test():
    pm = ProxyManager()
    pm.load_from_txt('proxies.txt', parse_pattern='login:password@ip:port')
    for i in range(15):
        async with pm.get('http_requests') as proxy:
            print(proxy)

asyncio.run(loop_test())
```

#### Output:
```
{'http': 'http://tuthixen:some_password@45.87.249.8:7586'}
{'http': 'http://tuthixen:some_password@45.87.249.44:7622'}
sleep
{'http': 'http://tuthixen:some_password@45.87.249.8:7586'}
{'http': 'http://tuthixen:some_password@45.87.249.44:7622'}
...
```

### Load from rows
```
rows = [
    '45.87.249.8:7586@tuthixen:some_password',
    '45.87.249.44:7622@tuthixen:some_password',
    '45.87.249.84:7662@tuthixen:some_password'
]
pm = ProxyManager()
pm.from_rows(rows, parse_pattern='ip:port@login:password')
for proxy in pm:
    print(proxy)
```

#### Output:
```
{'login': 'tuthixen', 'password': 'some_password', 'ip': '45.87.249.8', 'port': '7586'}
{'login': 'tuthixen', 'password': 'some_password', 'ip': '45.87.249.44', 'port': '7622'}
{'login': 'tuthixen', 'password': 'some_password', 'ip': '45.87.249.84', 'port': '7662'}
```

### set custom formatter
```
def custom_formatter(self):
    return [self.ip, self.port, self.login, self.password]
    
rows = [
    '45.87.249.8:7586@tuthixen:some_password',
    '45.87.249.44:7622@tuthixen:some_password',
    '45.87.249.84:7662@tuthixen:some_password'
] 
   
pm = ProxyManager()
pm.set_custom_formatter(custom_formatter)
pm.from_rows(rows, "ip:port@login:password")
for proxy in pm:
    print(proxy)
```

#### Output:

```
['45.87.249.8', '7586', 'tuthixen', 'some_password']
['45.87.249.44', '7622', 'tuthixen', 'some_password']
['45.87.249.84', '7662', 'tuthixen', 'some_password']
```

### set formatter
```
rows = [
    '45.87.249.8:7586@tuthixen:some_password',
    '45.87.249.44:7622@tuthixen:some_password',
    '45.87.249.84:7662@tuthixen:some_password'
] 
   
pm = ProxyManager()
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
```
#### Output:
```
{'login': 'tuthixen', 'password': 'some_password', 'ip': '45.87.249.8', 'port': '7586'}
{'login': 'tuthixen', 'password': 'some_password', 'ip': '45.87.249.44', 'port': '7622'}
{'login': 'tuthixen', 'password': 'some_password', 'ip': '45.87.249.84', 'port': '7662'}
switching formatter
sleep
http://tuthixen:some_password@45.87.249.84:7662
http://tuthixen:some_password@45.87.249.44:7622
http://tuthixen:some_password@45.87.249.8:7586
```