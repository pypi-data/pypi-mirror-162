# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['data_job_crawler',
 'data_job_crawler.crawler',
 'data_job_crawler.crawler.spiders']

package_data = \
{'': ['*'], 'data_job_crawler.crawler.spiders': ['data/*']}

install_requires = \
['Scrapy>=2.6.2,<3.0.0', 'playwright>=1.24.1,<2.0.0', 'psycopg2>=2.9.3,<3.0.0']

setup_kwargs = {
    'name': 'data-job-crawler',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Donor',
    'author_email': 'donorfelita@msn.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
