# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nerualpha',
 'nerualpha.providers',
 'nerualpha.providers.assets',
 'nerualpha.providers.logger',
 'nerualpha.providers.meetings',
 'nerualpha.providers.meetings.contracts',
 'nerualpha.providers.messages',
 'nerualpha.providers.messages.contracts',
 'nerualpha.providers.numbers',
 'nerualpha.providers.numbers.contracts',
 'nerualpha.providers.scheduler',
 'nerualpha.providers.scheduler.contracts',
 'nerualpha.providers.state',
 'nerualpha.providers.voice',
 'nerualpha.providers.voice.contracts',
 'nerualpha.providers.vonageAI',
 'nerualpha.providers.vonageAI.contracts',
 'nerualpha.providers.vonageAPI',
 'nerualpha.providers.vonageAPI.contracts',
 'nerualpha.request',
 'nerualpha.services',
 'nerualpha.services.commandService',
 'nerualpha.services.config',
 'nerualpha.services.jwt',
 'nerualpha.session',
 'nerualpha.webhookEvents',
 'nerualpha.webhookEvents.messenger',
 'nerualpha.webhookEvents.mms',
 'nerualpha.webhookEvents.sms',
 'nerualpha.webhookEvents.viber',
 'nerualpha.webhookEvents.whatsapp']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT[crypto]', 'aiohttp', 'pendulum', 'requests']

setup_kwargs = {
    'name': 'nerualpha',
    'version': '3.0.0',
    'description': 'neru-sdk for python developers',
    'long_description': '',
    'author': 'Sergei Rastrigin',
    'author_email': 'sergei.rastrigin@vonage.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
