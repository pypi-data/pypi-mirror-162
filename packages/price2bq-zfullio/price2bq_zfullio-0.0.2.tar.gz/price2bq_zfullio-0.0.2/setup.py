# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['price2bq_zfullio']

package_data = \
{'': ['*']}

install_requires = \
['bq-easy-zfullio>=0.0.3,<0.0.4',
 'loguru>=0.6.0,<0.7.0',
 'openpyxl>=3.0.10,<4.0.0',
 'pandas>=1.4.3,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'xlrd>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'price2bq-zfullio',
    'version': '0.0.2',
    'description': "Экспорт файлов c площадок 'Яндекс Недвижимость' и 'Циан' в BigQuery",
    'long_description': "# Price to BQ\n\nЭкспорт файлов c площадок 'Яндекс Недвижимость' и 'Циан' в BigQuery",
    'author': 'viktor',
    'author_email': 'vi.dave@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
