# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quranbot_schema_registry']

package_data = \
{'': ['*'],
 'quranbot_schema_registry': ['schemas/file/sendtriggered/*',
                              'schemas/mailing/created/*',
                              'schemas/messages/deleted/*',
                              'schemas/notification/created/*',
                              'schemas/websocket/notificationcreated/*']}

install_requires = \
['jsonschema>=4.7.2,<5.0.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'quranbot-schema-registry',
    'version': '0.0.9',
    'description': 'quranbot-schema-registry',
    'long_description': None,
    'author': 'Almaz Ilaletdinov',
    'author_email': 'a.ilaletdinov@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
