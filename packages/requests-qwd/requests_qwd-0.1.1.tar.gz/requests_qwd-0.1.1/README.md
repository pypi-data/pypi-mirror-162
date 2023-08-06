# requests_qwd

#### 介绍
requests_qwd魔改了requests库，使发出请求的同时记录请求消耗时间，并保存到本地文件

### 使用方式
```python
import requests_qwd as requests
r = requests.get(url,requests_name='该请求的代号',is_save_log=True,speed_log_path='./speed_log.log')
```

