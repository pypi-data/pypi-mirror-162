"""
    created 04.07.2022 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2022 by the django-fmd team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

__version__ = "0.3.1"

from pathlib import Path

import findmydevice


WEB_PATH = Path(findmydevice.__file__).parent / 'web'
assert WEB_PATH.is_dir(), f'Directory not found here: {WEB_PATH}'
