# Xj-User Module

> 用户模块



# Part 1. Introduce

> 介绍

- 本模块使用M工程化开发文档（MB 311-2022）标准编写

- 本模块采用MSA设计模式（MB 422-2022）



## Install

> 安装

- **依赖**

```
pip install djangorestframework==3.12.4
pip install PyJWT==2.3.0
```

- **/settings.py**

```python
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'apps.xj_user.apps.UserConfig',
]

```

- **/main/urls.py**

```python
from django.urls import include, re_path
urlpatterns = [
    ...,
    re_path(r'(api/)?xj_user/?', include('apps.xj_user.urls')),
]
```


