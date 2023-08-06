# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis', 'aleksis.apps.fritak', 'aleksis.apps.fritak.migrations']

package_data = \
{'': ['*'],
 'aleksis.apps.fritak': ['locale/ar/LC_MESSAGES/*',
                         'locale/de_DE/LC_MESSAGES/*',
                         'locale/fr/LC_MESSAGES/*',
                         'locale/la/LC_MESSAGES/*',
                         'locale/nb_NO/LC_MESSAGES/*',
                         'locale/tr_TR/LC_MESSAGES/*',
                         'templates/fritak/*']}

install_requires = \
['aleksis-core>=2.8,<3.0']

entry_points = \
{'aleksis.app': ['fritak = aleksis.apps.fritak.apps:FritakConfig']}

setup_kwargs = {
    'name': 'aleksis-app-fritak',
    'version': '2.0.1',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp Fritak (application management)',
    'long_description': 'AlekSIS\u200a—\u200aUnofficial App Fritak (exemption requests)\n====================================================\n\nAlekSIS\n-------\n\nThis is an **unofficial** application for use with the `AlekSIS`_ platform.\n\nFeatures\n--------\n\nThe Fritak app provides functionality for managing exemption requests.\n\nTypical Workflow\n~~~~~~~~~~~~~~~~\n\n1. Teacher fills out form with following fields:\n\n    - Start date and time\n    - End date and time\n    - Description/reason\n\n2. Headmaster receives request and a. approves or b. rejects:\n\n    a. Deputy headmaster reviews request and i. approves or ii. rejects:\n\n        i. Teacher receives positive feedback (notifcation).\n\n        ii. Teacher receives negative feedback (notification).\n\n    b. Teacher receives negative feedback (notification).\n\nLicence\n-------\n\n::\n\n  Copyright © 2017, 2018, 2019, 2020 Frank Poetzsch-Heffter <p-h@katharineum.de>\n  Copyright © 2017, 2018, 2019, 2020 Jonathan Weth <wethjo@katharineum.de>\n  Copyright © 2019 Julian Leucker <leuckeju@katharineum.de>\n  Copyright © 2019 Hangzhi Yu <yuha@katharineum.de>\n\n  Licenced under the EUPL, version 1.2 or later\n\nPlease see the LICENCE file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\n.. _AlekSIS: https://edugit.org/AlekSIS/AlekSIS\n.. _European Union Public Licence: https://eupl.eu/\n',
    'author': 'Julian Leucker',
    'author_email': 'leuckeju@katharineum.de',
    'maintainer': 'Frank Poetzsch-Heffter',
    'maintainer_email': 'p-h@katharineum.de',
    'url': 'https://aleksis.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
