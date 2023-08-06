# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slidge',
 'slidge.core',
 'slidge.plugins',
 'slidge.plugins.mattermost',
 'slidge.plugins.signal',
 'slidge.plugins.telegram',
 'slidge.util',
 'slidge.util.xep_0055',
 'slidge.util.xep_0077',
 'slidge.util.xep_0100',
 'slidge.util.xep_0115',
 'slidge.util.xep_0333',
 'slidge.util.xep_0356',
 'slidge.util.xep_0363']

package_data = \
{'': ['*']}

install_requires = \
['ConfigArgParse>=1.5.3,<2.0.0',
 'Pillow>=8.1.0',
 'aiohttp>=3.8.1',
 'qrcode>=7.3',
 'slixmpp>=1.8.2,<2.0.0']

extras_require = \
{'discord': ['nextcord>=2.0.0-alpha.10,<3.0.0'],
 'facebook': ['mautrix-facebook>=0.4.0,<0.5.0'],
 'mattermost': ['mattermost-api-reference-client>=4.0.0,<5.0.0'],
 'signal': ['aiosignald>=0.3.0alpha7,<0.4.0'],
 'skype': ['SkPy>=0.10.4,<0.11.0'],
 'steam': ['steam[client]>=1.3.0,<2.0.0'],
 'telegram': ['aiotdlib>=0.19.2,<0.20.0', 'pydantic']}

entry_points = \
{'console_scripts': ['slidge = slidge.__main__:main']}

setup_kwargs = {
    'name': 'slidge',
    'version': '0.1.0a2',
    'description': 'XMPP bridging framework',
    'long_description': 'Slidge 🛷\n========\n\n[Home](https://sr.ht/~nicoco/slidge) |\n[Source](https://sr.ht/~nicoco/slidge/sources) |\n[Issues](https://sr.ht/~nicoco/slidge/trackers) |\n[Patches](https://lists.sr.ht/~nicoco/public-inbox) |\n[Chat](xmpp:slidge@conference.nicoco.fr?join)\n\nTurn any XMPP client into that fancy multiprotocol chat app that every cool kid want.\n\n[![Documentation status](https://readthedocs.org/projects/slidge/badge/?version=latest)](https://slidge.readthedocs.io/)\n[![builds.sr.ht status](https://builds.sr.ht/~nicoco/slidge/commits/master/.build.yml.svg)](https://builds.sr.ht/~nicoco/slidge/commits/master/.build.yml?)\n[![pypi](https://badge.fury.io/py/slidge.svg)](https://pypi.org/project/slidge/)\n\nSlidge is a general purpose XMPP (puppeteer) gateway framework in python.\nIt\'s a work in progress, but it should make\n[writing gateways to other chat networks](https://slidge.readthedocs.io/en/latest/dev/tutorial.html)\n(*plugins*) as frictionless as possible.\n\nIt comes with a few plugins included.\n\n|            | Presences | Typing | Marks | Upload | Correction | Reactions |\n|------------|-----------|--------|-------|--------|------------|-----------|\n| Signal     | N/A       | ✓      | ✓     | ✓      | N/A        | ✓         |\n| Telegram   | ~         | ✓      | ✓     | ✓      | ✓          | ✓         |\n| Mattermost | ✓         | ✗      | ✗     | ✗      | ✗          | ✗         |\n| Facebook   | ✗         | ✓      | ✓     | ✓      | ✓          | ✗         |\n| Skype      | ✗         | ✗      | ✗     | ~      | ✗          | ✗         |\n\n(this table may not be entirely accurate, but **in theory**, stuff marked ✓ works)\n\n\nStatus\n------\n\nSlidge is alpha-grade software.\nRight now, only direct messages are implemented, no group chat stuff at all.\nDirect messaging does (more or less) work though.\nAny contribution whatsoever (testing, patches, suggestions, beer, …) is more than welcome.\nDon\'t be shy!\n\nTesting locally should be fairly easy, so please go ahead and give me some\nfeedback, through the [MUC](xmpp:slidge@conference.nicoco.fr?join), the\n[issue tracker](https://todo.sr.ht/~nicoco/slidge) or in my\n[public inbox](https://lists.sr.ht/~nicoco/public-inbox).\n\nInstallation\n------------\n\n#### docker-compose\n\nDocker-compose spins up a local XMPP server preconfigured for you., with a ``test@localhost`` / ``password``\naccount\n\n```\ndocker-compose up # or poetry install && poetry run `python -m slidge`\n```\n\nFor the other options, you need a\n[configured](https://slidge.readthedocs.io/en/latest/admin/general.html#configure-the-xmpp-server)\nXMPP server.\n\n#### poetry\n\n```\npoetry install\npoetry run python -m slidge\n```\n\n#### pip\n\n```bash\npip install slidge[signal]  # you can replace signal with any network listed in the table above\npython -m slidge --legacy-module=slidge.plugins.signal\n```\n\n### XMPP client\n\n#### movim\n\nIf you used docker-compose, you should be able to use the [movim](https://movim.eu) client\nfrom your browser at http://localhost:8888\n\nUnfortunately, the movim UI thinks that``test@localhost`` is not a valid JID and does not let you click\non the "Connect" button.\nAs a workaround, use your browser dev tools to inspect and modify the ``<input id="username"`` in order to\nremove the ``pattern="^[^...`` attribute.\n\nThen go to the Configuration/Account tab. You should be able to register to the slidge gateways from here.\n\n#### Gajim\n\nInstall and launch [gajim](https://gajim.org) and add your XMPP account.\nGo to "Accounts"→"Discover services" (or equivalent).\nYou should see the slidge gateways as server components.\n\nAbout privacy\n-------------\n\nSlidge (and most if not all XMPP gateway that I know of) will break\nend-to-end encryption, or more precisely one of the \'ends\' become the\ngateway itself. If privacy is a major concern for you, my advice would\nbe to:\n\n-   use XMPP + OMEMO\n-   self-host your gateways\n-   have your gateways hosted by someone you know AFK and trust\n\nRelated projects\n----------------\n\n-   [Spectrum](https://www.spectrum.im/)\n-   [Bitfrost](https://github.com/matrix-org/matrix-bifrost)\n-   [Mautrix](https://github.com/mautrix)\n-   [matterbridge](https://github.com/42wim/matterbridge)\n-   [XMPP-discord-bridge](https://git.polynom.me/PapaTutuWawa/xmpp-discord-bridge)\n',
    'author': 'Nicolas Cedilnik',
    'author_email': 'nicoco@nicoco.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sr.ht/~nicoco/slidge/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
