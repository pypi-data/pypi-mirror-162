# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['forgework', 'forgework.management', 'forgework.management.commands']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.0',
 'forge-core>=0.4.0,<1.0.0',
 'honcho>=1.1.0,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0']

entry_points = \
{'console_scripts': ['forge-work = forgework:cli']}

setup_kwargs = {
    'name': 'forge-work',
    'version': '0.3.0',
    'description': 'Work library for Forge',
    'long_description': '# forge-work\n\nA single command to run everything you need for Django development at once.\n\n![Forge work command example](https://user-images.githubusercontent.com/649496/176533533-cfd44dc5-afe5-42af-8b5d-33a9fa23f8d9.gif)\n\nThe following processes will run simultaneously (some will only run if they are detected as available):\n\n- [`manage.py runserver` (and migrations)](#runserver)\n- [`forge-db start --logs`](#forge-db)\n- [`forge-tailwind compile --watch`](#forge-tailwind)\n- [`npm run watch`](#package-json)\n- [`stripe listen --forward-to`](#stripe)\n- [`ngrok http --subdomain`](#ngrok)\n\n\n## Installation\n\n### Forge installation\n\nThe `forge-work` package is a dependency of [`forge`](https://github.com/forgepackages/forge) and is available as `forge work`.\n\nIf you use the [Forge quickstart](https://www.forgepackages.com/docs/quickstart/),\neverything you need will already be set up.\n\nThe [standard Django installation](#standard-django-installation) can give you an idea of the steps involved.\n\n\n### Standard Django installation\n\nThis package can be used without `forge` by installing it as a regular Django app.\n\nFirst, install `forge-work` from [PyPI](https://pypi.org/project/forge-work/):\n\n```sh\npip install forge-work\n```\n\nThen add it to your `INSTALLED_APPS` in `settings.py`:\n\n```python\nINSTALLED_APPS = [\n    ...\n    "forgework",\n]\n```\n\nNow instead of using the basic `manage.py runserver` (and a bunch of commands before and during that process), you can simply do:\n\n```sh\npython manage.py work\n```\n\n## Processes\n\n### Runserver\n\nThe key process here is still `manage.py runserver`.\nBut, before that runs, it will also wait for the database to be available and run `manage.py migrate`.\n\n### forge-db\n\nThe [`forge-db` package](https://github.com/forgepackages/forge-db) uses Docker to run a local Postgres database.\n\nIf `forge-db` is installed, it will automatically start and show the logs of the running database container.\n\n### forge-tailwind\n\nThe [`forge-tailwind` package](https://github.com/forgepackages/forge-tailwind) compiles Tailwind CSS using the Tailwind standalone CLI.\n\nIf `forge-tailwind` is installed, it will automatically run the Tailwind `compile --watch` process.\n\n### package.json\n\nIf a `package.json` file is found and contains a `watch` script,\nit will automatically run.\nThis is an easy place to run your own custom JavaScript watch process.\n\n### Stripe\n\nIf a `STRIPE_WEBHOOK_PATH` env variable is set then this will add a `STRIPE_WEBHOOK_SECRET` to `.env` (using `stripe listen --print-secret`) and it will then run `stripe listen --forward-to <runserver:port/stripe-webhook-path>`.\n\n### Ngrok\n\nIf an `NGROK_SUBDOMAIN` env variable is set then this will run `ngrok http <runserver_port> --subdomain <subdomain>`.\n',
    'author': 'Dave Gaeddert',
    'author_email': 'dave.gaeddert@dropseed.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.forgepackages.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
