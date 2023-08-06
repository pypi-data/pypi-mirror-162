# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis',
 'aleksis.apps.buelleten',
 'aleksis.apps.buelleten.migrations',
 'aleksis.apps.buelleten.models']

package_data = \
{'': ['*'],
 'aleksis.apps.buelleten': ['locale/*',
                            'locale/ar/LC_MESSAGES/*',
                            'locale/de_DE/LC_MESSAGES/*',
                            'locale/fr/LC_MESSAGES/*',
                            'locale/la/LC_MESSAGES/*',
                            'locale/nb_NO/LC_MESSAGES/*',
                            'locale/tr_TR/LC_MESSAGES/*',
                            'static/*',
                            'templates/buelleten/display/*',
                            'templates/buelleten/display_group/*',
                            'templates/buelleten/slide/*']}

install_requires = \
['aleksis-core>=2.7,<3.1']

entry_points = \
{'aleksis.app': ['buelleten = aleksis.apps.buelleten.apps:DefaultConfig']}

setup_kwargs = {
    'name': 'aleksis-app-buelleten',
    'version': '1.0.7.dev0',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp Bülleten (Digital Signage)',
    'long_description': 'AlekSIS (School Information System)\u200a—\u200aApp Bülleten (Digital Signage)\n==================================================================================================\n\nAlekSIS\n-------\n\nThis is an application for use with the `AlekSIS®`_ platform.\n\nFeatures\n--------\n\nThe author of this app did not describe it yet.\n\nLicence\n-------\n\n::\n\n  Copyright © 2021 Jonathan Weth <dev@jonathanweth.de>\n  Copyright © 2022 Dominik George <dominik.george@teckids.org>\n  Copyright © 2022 Tom Teichler <tom.teichler@teckids.org>\n\n  Licenced under the EUPL, version 1.2 or later\n\nPlease see the LICENCE.rst file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\nTrademark\n---------\n\nAlekSIS® is a registered trademark of the AlekSIS open source project, represented\nby Teckids e.V. Please refer to the `trademark policy`_ for hints on using the trademark\nAlekSIS®.\n\n.. _AlekSIS®: https://edugit.org/AlekSIS/AlekSIS\n.. _European Union Public Licence: https://eupl.eu/\n.. _trademark policy: https://aleksis.org/pages/about\n',
    'author': 'Tom Teichler',
    'author_email': 'tom.teichler@teckids.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://aleksis.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
