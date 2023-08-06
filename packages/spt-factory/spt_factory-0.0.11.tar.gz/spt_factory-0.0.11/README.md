
## Либка для получения доступа к ресурсам spt

Один раз инициализируете фабрику и потом с помощью методов `get_<recource_name>`(получить креды `get_<recource_name>_credentials`) получаете наобходимый доступ без прописывания всех логинов, явок, паролей

Реализованные ресурсы на текущий момент:

 - potok-stage-db (psycopg2 edition) по умолчанию подключается к moniback-new

## Пример использования

Необходимо установить сертификат:

```bash
sudo mkdir -p /usr/local/share/ca-certificates/Yandex && \
sudo wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" -O /usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt
```

Так же необходимо указать две переменные окружения: 

 - MONGO_URL=<url>
 - SSLROOT=/usr/local/share/ca-certificates/Yandex/YandexInternalRootCA.crt



```python
import os
from spt_factory import MongoFactory as SPTFactory

f = SPTFactory(
    mongo_url=os.getenv('MONGO_URL'),
    tlsCAFile=os.getenv('SSLROOT'),
)

print(f.get_postgres_credentials())

with f.get_postgres(dbname='moniback') as conn:
    print("Happy coding")
```

## Работа с локальными ресурсами

При вызове получения ресурса вы можете переписать значения из монги своими значениями:

```python
import os
from spt_factory import MongoFactory as SPTFactory

f = SPTFactory(
    mongo_url=os.getenv('MONGO_URL'),
    tlsCAFile=os.getenv('SSLROOT'),
)

params = {
    'host': 'localhost',
    'port': '5432',
    ...
} if os.getenv('ENV') == 'LOCAL' else {} 

print(f.get_postgres_credentials(**params))

with f.get_postgres(dbname='moniback') as conn:
    print("Happy coding")
```


## DS часть

Фабрика позволяет получить доступ к `ModelManager` & `PipelineManager`, которые являются singleton'ами

```python
...
# Вернет один и тот же объект
model_manager_1 = f.get_model_manager()
model_manager_2 = f.get_model_manager()

# Вернет один и тот же объект
pipeline_manager_1 = f.get_pipeline_manager()
pipeline_manager_2 = f.get_pipeline_manager()
```


## Работа с хранилищем S3

Также можно получить доступ к хранилищу S3 посредством фабрики и загружать или выгружать файлы с хранилища.

Метод `upload_file` позволяет загрузить в хранилище любой readable object. 

В тоже время `upload_binstr` позволяет загрузить в хранилище только бинарный файл.

Метод `download_file` загружает файл на ваше устройство.

`download_bin` загружает бинарный файл на ваше устройство.

```python
import os
from spt_factory.factory import MongoFactory as SPTFactory


s = b'example string'
f = SPTFactory(
    mongo_url=os.getenv('MONGO_URL'),
    tlsCAFile=os.getenv('SSLROOT'),
)
manager = f.get_s3_manager()
manager.upload_binstr(bucket_name='theme-models', id='91', bin_str=s)
manager.upload_file(bucket_name='theme-models', id='92', filepath='test.py', author='Walle')
manager.download_file(bucket_name='theme-models', id='1', filepath='../downloaded_file.txt')
data = manager.download_bin('theme-models', '91')
print(data)
```