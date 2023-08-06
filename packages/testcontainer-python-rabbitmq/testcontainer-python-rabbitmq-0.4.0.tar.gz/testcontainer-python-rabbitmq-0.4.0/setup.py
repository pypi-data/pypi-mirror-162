# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['testcontainer_python_rabbitmq']

package_data = \
{'': ['*']}

install_requires = \
['testcontainers>=3.6.0,<4.0.0']

setup_kwargs = {
    'name': 'testcontainer-python-rabbitmq',
    'version': '0.4.0',
    'description': 'Testcontainer for RabbitMQ',
    'long_description': '# Python Testcontainer RabbitMQ\n\n## Usage\n\n```python\nimport pika\nfrom testcontainer_python_rabbitmq import RabbitMQContainer\n\n\ndef test_rabbitmq():\n    config = RabbitMQContainer()\n    with config as container:\n        connection = pika.BlockingConnection(\n            pika.ConnectionParameters(\n                host=container.get_container_host_ip(),\n                port=container.get_amqp_port(),\n                credentials=pika.PlainCredentials(username="guest", password="guest"),\n            )\n        )\n\n        # do something...\n```\n',
    'author': 'Max Fröhlich',
    'author_email': 'max.froehlich@serviceware.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
