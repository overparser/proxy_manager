
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
for proxy in pm:
    with pm.get() as proxy:
    print(proxy)

print('switching formatter')
pm.set_formatter('aiohttp')
for proxy in pm:
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