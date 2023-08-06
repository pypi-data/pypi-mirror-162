## D:\work\mwwork\JTT\jtt-tm-util
#### jtt 常用工具
* 

### 设计


### 设定
*

###产生分发包
``
python setup.py sdist
twine upload dist/*
``
### 运行
* python setup.py sdist build
* python setup.py install


### 修改记录
* 2020/03/23
```text
  v 0.0.4
  修改consul reader 增加read_service 的key参数,向上兼容 

```
* 2020/05/27
```text
  v 0.0.5
  修改consul reader 增加service_as_url向上兼容 

```

* 2020/06/11
```text
  v 0.0.6
  
  修改sync_basedata 增加read employee
```

* 2020/06/17
```text
  v 0.0.7
  
  修改sync_basedata 的bug