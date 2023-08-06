# Django Find My Device

![django-fmd @ PyPi](https://img.shields.io/pypi/v/django-fmd?label=django-fmd%20%40%20PyPi)
![Python Versions](https://img.shields.io/pypi/pyversions/django-fmd)
![License GPL V3+](https://img.shields.io/pypi/l/django-fmd)

Find My Device client and server implemented in Python using Django.
Usable for the Andorid App [**FindMyDevice**](https://gitlab.com/Nulide/findmydevice/) by [Nnulide](https://nulide.de/):

[<img src="https://fdroid.gitlab.io/artwork/badge/get-it-on.png" alt="Get FindMyDevice on F-Droid" height="80">](https://f-droid.org/packages/de.nulide.findmydevice/)

Note: For command notifications, you also need to install a https://unifiedpush.org/ app like "ntfy":

[<img src="https://fdroid.gitlab.io/artwork/badge/get-it-on.png" alt="Get ntfy on F-Droid" height="80">](https://f-droid.org/packages/io.heckel.ntfy)


# Django "Find My Device" server for YunoHost

[![Integration level](https://dash.yunohost.org/integration/django-fmd.svg)](https://dash.yunohost.org/appci/app/django-fmd) ![Working status](https://ci-apps.yunohost.org/ci/badges/django-fmd.status.svg) ![Maintenance status](https://ci-apps.yunohost.org/ci/badges/django-fmd.maintain.svg)
[![Install django-fmd with YunoHost](https://install-app.yunohost.org/install-with-yunohost.svg)](https://install-app.yunohost.org/?app=django-fmd)

## State

### Server implementation

What worked:

* App can register the device
* App can send a new location
* App can delete all server data by unregister the device
* The Web page can fetch the location of a device
* Paginate between locations in Web page
* Push notification of commands

Server TODOs:

* Pictures

### Client implementation

See demo: https://gitlab.com/jedie/django-find-my-device/-/blob/main/fmd_client_demo.py

What worked:

* Register on server
* Send location to server
* Get location from server
* Delete device on server

Client implementation TODOs:

* A usable CLI
* notification
* Pictures


## Start hacking:

```bash
~$ git clone https://gitlab.com/jedie/django-find-my-device.git
~$ cd django-find-my-device
~/django-find-my-device$ ./devshell.py
...
(findmydevice) run_testserver
```

## credits

The *FindMyDevice* concept and the App/Web pages credits goes to [Nnulide](https://nulide.de/) the creator of the app FindMyDevice.

Currently, we store a copy of html/js/css etc. files from [findmydeviceserver/web/](https://gitlab.com/Nulide/findmydeviceserver/-/tree/master/web) ([GNU GPLv3](https://gitlab.com/Nulide/findmydeviceserver/-/blob/master/LICENSE))
into our project repository here: [django-find-my-device/findmydevice/web/](https://gitlab.com/jedie/django-find-my-device/-/tree/main/findmydevice/web)
with the [update_fmdserver_files.sh](https://gitlab.com/jedie/django-find-my-device/-/blob/main/update_fmdserver_files.sh) script.


Some external files are added to this git repository, e.g.:

* `crypto-js` (MIT License) - https://github.com/brix/crypto-js
* `JSEncrypt` (MIT License) - https://github.com/travist/jsencrypt
* `Leaflet` (BSD 2-Clause "Simplified" License) - http://leafletjs.com - https://github.com/Leaflet/Leaflet
* `toastedjs`  (MIT License) - https://github.com/shakee93/toastedjs


## versions

* [*dev*](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.3.2...main)
  * TBC
* [v0.3.2 - 10.08.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.3.1...v0.3.2)
  * Bugfix to small database fields
  * Test project auto login only for `/admin/` requests
* [v0.3.1 - 10.08.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.3.0...v0.3.1)
  * Bugfix static files for YunoHost
* [v0.3.0 - 10.08.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.2.0...v0.3.0)
  * WIP: FMD python client (TODO: Add a CLI)
  * Replace the device `UUID` with a short random string
  * Include external JS/CSS files
* [v0.2.0 - 19.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.1.3...v0.2.0)
  * Store User-Agent in Device and LocationData
  * Implement command push notifications
* [v0.1.3 - 12.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.1.2...v0.1.3)
  * Remove "@Nulide FMDServer" from index.html
  * Lower 'No "IDT"' error log.
* [v0.1.2 - 12.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.1.1...v0.1.2)
  * Enhance Device change list: LocationData count + last update info and LocationData filter
  * Add login page for anonymous users
* [v0.1.1 - 12.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.1.0...v0.1.1)
  * Fix pagination on FMD web page.
  * Deny store locations too often (by `settings.FMD_MIN_LOCATION_DATE_RANGE_SEC` - default: 30sec.)
  * Display device date in admin in human-readable format.
  * Allow `location` delete in admin if `DEBUG` mode is on.
  * More tolerant `/requestAccess` view.
  * Enhance `TracingMiddleware` for debugging.
* [v0.1.0 - 12.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.0.4...v0.1.0)
  * Serve fmd page "index.html" with own view and only for authenticated users
  * Enhance Django Admin
  * Add optional "name" for Devices (Only for django admin)
* [v0.0.4 - 11.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.0.3...v0.0.4)
  * Bugfix `logic.js` requests, if installed not in root URL.
  * Bugfix location view from `logic.js` and undefined variable.
* [v0.0.3 - 11.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.0.2...v0.0.3)
  * Bugfix store location because of too large `raw_date` field value
* [v0.0.2 - 11.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/v0.0.1...v0.0.2)
  * Support Python 3.7 (for current YunoHost version)
  * Setup Gitlab CI pipeline
  * Update README
* [v0.0.1 - 05.07.2022](https://gitlab.com/jedie/django-find-my-device/-/compare/11d09ecb...v0.0.1)
  * init project
  * App can register the device
  * App can send a new location
  * App can delete all server data from the device
  * The Web page can fetch the location of a devi

