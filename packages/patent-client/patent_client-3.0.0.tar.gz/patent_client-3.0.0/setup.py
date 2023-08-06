# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['patent_client',
 'patent_client.epo',
 'patent_client.epo.family',
 'patent_client.epo.legal',
 'patent_client.epo.number_service',
 'patent_client.epo.published',
 'patent_client.epo.published.model',
 'patent_client.epo.published.schema',
 'patent_client.usitc',
 'patent_client.uspto',
 'patent_client.uspto.assignment',
 'patent_client.uspto.fulltext',
 'patent_client.uspto.fulltext.patent',
 'patent_client.uspto.fulltext.published_application',
 'patent_client.uspto.fulltext.schema',
 'patent_client.uspto.peds',
 'patent_client.uspto.ptab',
 'patent_client.util',
 'patent_client.util.base',
 'patent_client.util.claims']

package_data = \
{'': ['*'],
 'patent_client.epo.family': ['test/*', 'test/expected/*'],
 'patent_client.epo.legal': ['test/example.xml',
                             'test/example.xml',
                             'test/expected/*',
                             'test/us_example.xml',
                             'test/us_example.xml'],
 'patent_client.epo.published': ['test/*', 'test/expected/*'],
 'patent_client.uspto.assignment': ['test/*'],
 'patent_client.uspto.fulltext': ['examples/*'],
 'patent_client.uspto.fulltext.patent': ['test/*'],
 'patent_client.uspto.fulltext.published_application': ['test/*'],
 'patent_client.uspto.peds': ['test/*'],
 'patent_client.util.claims': ['examples/*']}

install_requires = \
['PyPDF2>=2.2.0,<3.0.0',
 'colorlog>=6.6.0,<7.0.0',
 'inflection>=0.5.1,<0.6.0',
 'lxml>=4.9.0,<5.0.0',
 'openpyxl>=3.0.10,<4.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests-cache>=0.9.4,<0.10.0',
 'requests>=2.28.0,<3.0.0',
 'yankee>=0.1.30,<0.2.0']

setup_kwargs = {
    'name': 'patent-client',
    'version': '3.0.0',
    'description': 'A set of ORM-style clients for publicly available intellectual property data',
    'long_description': None,
    'author': 'Parker Hancock',
    'author_email': '633163+parkerhancock@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
