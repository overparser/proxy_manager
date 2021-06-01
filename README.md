
#Context_manager
```
pm = ProxyManager()
pm.load_from_txt('proxies.txt', parse_pattern='login:password@ip:port')

for i in range(15):
    with pm.get('http_requests') as proxy:
        print(proxy)
```

Output:
```
>:
{'http': 'http://tuthixen:some_password@45.87.249.8:7586'}
{'http': 'http://tuthixen:some_password@45.87.249.44:7622'}
{'http': 'http://tuthixen:some_password@45.87.249.84:7662'}
{'http': 'http://tuthixen:some_password@45.87.249.134:7712'}
{'http': 'http://tuthixen:some_password@45.87.249.80:7658'}
{'http': 'http://tuthixen:some_password@45.87.249.88:7666'}
{'http': 'http://tuthixen:some_password@45.87.249.173:7751'}
{'http': 'http://tuthixen:some_password@45.87.249.85:7663'}
{'http': 'http://tuthixen:some_password@45.87.249.112:7690'}
{'http': 'http://tuthixen:some_password@45.87.249.254:7832'}
sleep
{'http': 'http://tuthixen:some_password@45.87.249.254:7832'}
{'http': 'http://tuthixen:some_password@45.87.249.112:7690'}
{'http': 'http://tuthixen:some_password@45.87.249.85:7663'}
{'http': 'http://tuthixen:some_password@45.87.249.173:7751'}
...
```

#Async context_manager
```
async def loop_test():
    pm = ProxyManager()
    pm.load_from_txt('proxies.txt', parse_pattern='login:password@ip:port')
    for i in range(15):
        async with pm.get('http_requests') as proxy:
            print(proxy)

asyncio.run(loop_test())
```

Output:
```
>:
{'http': 'http://tuthixen:some_password@45.87.249.8:7586'}
{'http': 'http://tuthixen:some_password@45.87.249.44:7622'}
{'http': 'http://tuthixen:some_password@45.87.249.84:7662'}
{'http': 'http://tuthixen:some_password@45.87.249.134:7712'}
{'http': 'http://tuthixen:some_password@45.87.249.80:7658'}
{'http': 'http://tuthixen:some_password@45.87.249.88:7666'}
{'http': 'http://tuthixen:some_password@45.87.249.173:7751'}
{'http': 'http://tuthixen:some_password@45.87.249.85:7663'}
{'http': 'http://tuthixen:some_password@45.87.249.112:7690'}
{'http': 'http://tuthixen:some_password@45.87.249.254:7832'}
asleep
{'http': 'http://tuthixen:some_password@45.87.249.254:7832'}
{'http': 'http://tuthixen:some_password@45.87.249.112:7690'}
{'http': 'http://tuthixen:some_password@45.87.249.85:7663'}
{'http': 'http://tuthixen:some_password@45.87.249.173:7751'}
...
```

#Load from rows
```
rows = [
    '45.87.249.8:7586@tuthixen:some_password',
    '45.87.249.44:7622@tuthixen:some_password',
    '45.87.249.84:7662@tuthixen:some_password'
]
pm = ProxyManager()
pm.from_rows(rows, parse_pattern='ip:port@login:password')
```