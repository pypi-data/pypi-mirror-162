# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['findmydevice',
 'findmydevice.admin',
 'findmydevice.management',
 'findmydevice.management.commands',
 'findmydevice.migrations',
 'findmydevice.models',
 'findmydevice.services',
 'findmydevice.views',
 'findmydevice_project',
 'findmydevice_project.settings',
 'findmydevice_project.tests',
 'findmydevice_project.tests.fixtures',
 'fmd_client']

package_data = \
{'': ['*'],
 'findmydevice': ['static/fmd_externals/*',
                  'static/fmd_externals/assets/*',
                  'templates/fmd/*',
                  'web/*'],
 'findmydevice_project': ['templates/admin/*'],
 'findmydevice_project.tests.fixtures': ['device1/*']}

install_requires = \
['bx_django_utils',
 'bx_py_utils',
 'colorlog',
 'django',
 'django-debug-toolbar',
 'django-tools',
 'pycryptodomex',
 'requests']

entry_points = \
{'console_scripts': ['devshell = '
                     'findmydevice_project.dev_shell:devshell_cmdloop',
                     'run_testserver = '
                     'findmydevice_project.manage:start_test_server']}

setup_kwargs = {
    'name': 'django-fmd',
    'version': '0.3.0',
    'description': "Server for 'Find My Device' android app, implemented in Django/Python",
    'long_description': '# Django Find My Device\n\n![django-fmd @ PyPi](https://img.shields.io/pypi/v/django-fmd?label=django-fmd%20%40%20PyPi)\n![Python Versions](https://img.shields.io/pypi/pyversions/django-fmd)\n![License GPL V3+](https://img.shields.io/pypi/l/django-fmd)\n\nFind My Device client and server implemented in Python using Django.\nUsable for the Andorid App [**FindMyDevice**](https://gitlab.com/Nulide/findmydevice/) by [Nnulide](https://nulide.de/):\n\n[<img src="https://fdroid.gitlab.io/artwork/badge/get-it-on.png" alt="Get FindMyDevice on F-Droid" height="80">](https://f-droid.org/packages/de.nulide.findmydevice/)\n\nNote: For command notifications, you also need to install a https://unifiedpush.org/ app like "ntfy":\n\n[<img src="https://fdroid.gitlab.io/artwork/badge/get-it-on.png" alt="Get ntfy on F-Droid" height="80">](https://f-droid.org/packages/io.heckel.ntfy)\n\n\n# Django "Find My Device" server for YunoHost\n\n[![Integration level](https://dash.yunohost.org/integration/django-fmd.svg)](https://dash.yunohost.org/appci/app/django-fmd) ![Working status](https://ci-apps.yunohost.org/ci/badges/django-fmd.status.svg) ![Maintenance status](https://ci-apps.yunohost.org/ci/badges/django-fmd.maintain.svg)\n[![Install django-fmd with YunoHost](https://install-app.yunohost.org/install-with-yunohost.svg)](https://install-app.yunohost.org/?app=django-fmd)\n\n## State\n\n### Server implementation\n\nWhat worked:\n\n* App can register the device\n* App can send a new location\n* App can delete all server data by unregister the device\n* The Web page can fetch the location of a device\n* Paginate between locations in Web page\n* Push notification of commands\n\nServer TODOs:\n\n* Pictures\n\n### Client implementation\n\nSee demo: https://gitlab.com/jedie/django-find-my-device/-/blob/main/fmd_client_demo.py\n\nWhat worked:\n\n* Register on server\n* Send location to server\n* Get location from server\n* Delete device on server\n\nClient implementation TODOs:\n\n* A usable CLI\n* notification\n* Pictures\n\n\n## Start hacking:\n\n```bash\n~$ git clone https://gitlab.com/jedie/django-find-my-device.git\n~$ cd django-find-my-device\n~/django-find-my-device$ ./devshell.py\n...\n(findmydevice) run_testserver\n```\n\n## credits\n\nThe *FindMyDevice* concept and the App/Web pages credits goes to [Nnulide](https://nulide.de/) the creator of the app FindMyDevice.\n\nCurrently, we store a copy of html/js/css etc. files from [findmydeviceserver/web/](https://gitlab.com/Nulide/findmydeviceserver/-/tree/master/web) ([GNU GPLv3](https://gitlab.com/Nulide/findmydeviceserver/-/blob/master/LICENSE))\ninto our project repository here: [django-find-my-device/findmydevice/web/](https://gitlab.com/jedie/django-find-my-device/-/tree/main/findmydevice/web)\nwith the [update_fmdserver_files.sh](https://gitlab.com/jedie/django-find-my-device/-/blob/main/update_fmdserver_files.sh) script.\n\n\nSome external files are added to this git repository, e.g.:\n\n* `crypto-js` (MIT License) - https://github.com/brix/crypto-js\n* `JSEncrypt` (MIT License) - https://github.com/travist/jsencrypt\n* `Leaflet` (BSD 2-Clause "Simplified" License) - http://leafletjs.com - https://github.com/Leaflet/Leaflet\n* `toastedjs`  (MIT License) - https://github.com/shakee93/toastedjs\n\n\n## versions\n\n* [*dev*](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.3.0...main)\n  * TBC\n* [v0.3.0 - 10.08.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.2.0...v0.3.0)\n  * WIP: FMD python client (TODO: Add a CLI)\n  * Replace the device `UUID` with a short random string\n  * Include external JS/CSS files\n* [v0.2.0 - 19.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.1.3...v0.2.0)\n  * Store User-Agent in Device and LocationData\n  * Implement command push notifications\n* [v0.1.3 - 12.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.1.2...v0.1.3)\n  * Remove "@Nulide FMDServer" from index.html\n  * Lower \'No "IDT"\' error log.\n* [v0.1.2 - 12.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.1.1...v0.1.2)\n  * Enhance Device change list: LocationData count + last update info and LocationData filter\n  * Add login page for anonymous users\n* [v0.1.1 - 12.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.1.0...v0.1.1)\n  * Fix pagination on FMD web page.\n  * Deny store locations too often (by `settings.FMD_MIN_LOCATION_DATE_RANGE_SEC` - default: 30sec.)\n  * Display device date in admin in human-readable format.\n  * Allow `location` delete in admin if `DEBUG` mode is on.\n  * More tolerant `/requestAccess` view.\n  * Enhance `TracingMiddleware` for debugging.\n* [v0.1.0 - 12.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.0.4...v0.1.0)\n  * Serve fmd page "index.html" with own view and only for authenticated users\n  * Enhance Django Admin\n  * Add optional "name" for Devices (Only for django admin)\n* [v0.0.4 - 11.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.0.3...v0.0.4)\n  * Bugfix `logic.js` requests, if installed not in root URL.\n  * Bugfix location view from `logic.js` and undefined variable.\n* [v0.0.3 - 11.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.0.2...v0.0.3)\n  * Bugfix store location because of too large `raw_date` field value\n* [v0.0.2 - 11.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.0.1...v0.0.2)\n  * Support Python 3.7 (for current YunoHost version)\n  * Setup Gitlab CI pipeline\n  * Update README\n* [v0.0.1 - 05.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/11d09ecb...v0.0.1)\n  * init project\n  * App can register the device\n  * App can send a new location\n  * App can delete all server data from the device\n  * The Web page can fetch the location of a devi\n\n',
    'author': 'JensDiemer',
    'author_email': 'git@jensdiemer.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/jedie/django-find-my-device',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0.0',
}


setup(**setup_kwargs)
