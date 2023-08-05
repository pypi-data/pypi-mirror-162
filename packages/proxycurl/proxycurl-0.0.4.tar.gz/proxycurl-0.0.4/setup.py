# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['proxycurl', 'proxycurl.asyncio', 'proxycurl.gevent', 'proxycurl.twisted']

package_data = \
{'': ['*']}

extras_require = \
{'asyncio': ['asyncio>=3.4.3,<4.0.0', 'aiohttp>=3.7.4,<4.0.0'],
 'gevent': ['gevent>=21.1.1,<22.0.0', 'requests>=2.25.0,<3.0.0'],
 'twisted': ['Twisted>=21.7.0,<22.0.0', 'treq>=21.5.0,<22.0.0']}

setup_kwargs = {
    'name': 'proxycurl',
    'version': '0.0.4',
    'description': 'Proxycurl is a set of tools designed to serve as plumbing for fresh and processed data in your application',
    'long_description': "# Proxycurl\n## What is it?\n**Proxycurl** is a set of tools designed to serve as plumbing for fresh and processed data in your application. We sit as a fully-managed layer between your application and raw data so that you can focus on building the application instead of worrying about scraping and processing data at scale.\n\n### With Proxycurl, you can\n - Lookup people\n - Lookup companies\n - Enrich people profiles\n - Enrich company profiles\n - Lookup contact information on people and companies\n - Check if an email address is of a disposable nature\n\nVisit [Proxycurl Official Web](https://nubela.co/proxycurl) for more details.\n\n## Usage\n```sh\n# PyPI\npip install proxycurl\n```\n* Make sure you set environtment `PROXYCURL_API_KEY` variable see `proxycurl/config.py`\n* You can get `PROXYCURL_API_KEY` in [Proxycurl Official Web](https://nubela.co/proxycurl/auth/register)\n\n## Example\nAfter you install the library you can use like the example that provided each concurrent method:\n\n### Gevent\n```sh\n# install required library\npip install 'proxycurl[gevent]'\npython examples/lib-gevent.py\n```\n### Twisted\n```sh\n# install required library\npip install 'proxycurl[asyncio]'\npython examples/lib-twisted.py\n```\n### Asyncio\n```sh\n# install required library\npip install 'proxycurl[asyncio]'\npython examples/lib-asyncio.py\n```",
    'author': 'Nubela',
    'author_email': 'tech@nubela.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
