# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['taskiq_aio_pika', 'taskiq_aio_pika.tests']

package_data = \
{'': ['*']}

install_requires = \
['aio-pika>=8.1.0,<9.0.0', 'taskiq>=0,<1']

setup_kwargs = {
    'name': 'taskiq-aio-pika',
    'version': '0.0.2',
    'description': 'RabbitMQ broker for taskiq',
    'long_description': '# AioPika broker for taskiq\n\nThis lirary provides you with aio-pika broker for taskiq.\n\nUsage:\n```python\nfrom taskiq_aio_pika import AioPikaBroker\n\nbroker = AioPikaBroker()\n\n@broker.task\nasync def test() -> None:\n    print("nothing")\n\n```\n\n\n## Configuration\n\nAioPikaBroker parameters:\n* `url` - url to rabbitmq. If None, "amqp://guest:guest@localhost:5672" is used.\n* `result_backend` - custom result backend.\n* `task_id_generator` - custom task_id genertaor.\n* `exchange_name` - name of exchange that used to send messages.\n* `exchange_type` - type of the exchange. Used only if `declare_exchange` is True.\n* `queue_name` - queue that used to get incoming messages.\n* `routing_key` - that used to bind that queue to the exchange.\n* `declare_exchange` - whether you want to declare new exchange if it doesn\'t exist.\n* `qos` - number of messages that worker can prefetch.\n* `max_connection_pool_size` - maximum number of connections in pool.\n* `max_channel_pool_size` - maximum number of channels for each connection.\n',
    'author': 'Pavel Kirilin',
    'author_email': 'win10@list.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/taskiq-python/taskiq-aio-pika',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
