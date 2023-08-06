# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lt_autosnap']

package_data = \
{'': ['*']}

install_requires = \
['single-version>=1.5.1,<2.0.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.8,<0.9']}

entry_points = \
{'console_scripts': ['ltautosnap = lt_autosnap.cli:cli']}

setup_kwargs = {
    'name': 'lt-autosnap',
    'version': '0.1.2a8',
    'description': 'LVM snapshot automation based on smbsnap from Samba.org',
    'long_description': "# lt-autosnap\n\n## DISCLAIMER\n\nDue to the following factors:\n\n- This software is intended to be run with root privileges\n- This software manages logical volumes on your machine, including creationg and deletion of snapshots\n- There may be bugs in this software\n\n...be advised that this software has the ability to at the least cause you **DATA LOSS** and at the worst\n**SEVERELY DAMAGE OR IMPAIR** your operating system. **THIS IS NOT BACKUP SOFTWARE**.\n\nSee [LICENSE.txt](LICENSE.txt) for further disclaimers.\n\n## Introduction\n\nThe purpose of this tool is to automate management of LVM thin pool snapshots. It is intended to be used with\ncron or systemd timers for scheduling.\n\n[There is a guide on the Samba\nwebsite](https://wiki.samba.org/index.php/Rotating_LVM_snapshots_for_shadow_copy) for setting up rotating LVM\nsnapshots for use with Samba's implementation of Volume Shadow Copy. This script is based on the Bash script\nin that guide. It can mount snapshots to a specified path with dirnames compatible with Volume Shadow Copy,\ne.g. `@GMT-2022.04.28-22.35.17`. For more on setting up Samba for shadow copies, see\n[https://www.samba.org/samba/docs/current/man-html/vfs_shadow_copy2.8.html](https://www.samba.org/samba/docs/current/man-html/vfs_shadow_copy2.8.html)\n\n## Requirements\n\nThis tool requires Python 3.6 or later. For recent Linux distributions the system Python interpreter should\nsuffice. `pip` or `pip3` is required for installation, so you may need to install `python3-pip` or similar\npackage.\n\n### Python Dependencies\n\nSince I expect this to be a system package, I tried to minimize the dependencies it would install.\n\n- If you are using Python 3.6, pip will install the `dataclasses` backport for 3.6.\n- pip will install `single-version` for package version management.\n\n## Installation\n\nThis is a rare case of installing something with Python's `pip` as root.\n\n```bash\nsudo pip install lt-autosnap\n# --or--\nsudo pip3 install lt-autosnap\n```\n\n## Configuration\n\nCreate a config file with `ltautosnap genconf > ltautosnap.conf`. The comments provide guidance on how to\nconfigure volumes and snap sets. Modify the config file with the details about your volumes and desired snap\nset and, as root, copy it to `/etc/ltautosnap.conf`.\n\n## Usage\n\nMost commands require root privileges, even `list`, since it runs `lvs` which usually requires root.\n\n- Run `ltautosnap -h` for a list of all commands.\n- As root, create a crontab file at `/etc/cron.d/ltautosnap` to generate snaps.\n\n   Examples:\n\n   ```bash\n   # If desired, set an email address to send error messages\n   #   Cron will usually email stdout and stderr if you have mail set up with\n   #   Postfix or similar MTA.\n   MAILTO=example@example.org\n\n   # Generate a snapshot for vol0, set0 every day at midnight, no matter what\n   0 0 * * *  root ltautosnap snap 0 0\n\n   # Every hour at 3 minutes after the hour, for vol0, set1, if a period has\n   #   elapsed since the last snap of the set, create another one.\n   3 * * * *  root ltautosnap autosnap 0 1\n\n   # Every day at 3 AM remove all extra snaps (beyond each snapset's count)\n   #   starting with the oldest\n   0 3 * * *  root ltautosnap clean all\n\n   # Every hour at 5 after, for volume 1, automatically create new snaps as needed\n   #   and clean old ones for all snap sets.\n   5 0 * * *  root ltautosnap autosnap 1 --autoclean\n\n   # Every day at noon, check if each volume's pool has exceeded the warning level\n   #   This will log a warning to stderr if the warning level has been exceeded.\n   #   If MAILTO is set and your MTA is configured, you'll be emailed only if the\n   #   warning percent is exceeded.\n   0 12 * * *  root ltautosnap check all\n\n   # On the first day of the month, do the same but print the % used space to\n   #   stderr no matter what. If MAILTO is set and your MTA is configued, you'll\n   #   be emailed the volume usage every month.\n   0 0 1 * *  root ltautosnap check all -v\n   ```\n",
    'author': 'Randall Pittman',
    'author_email': 'randall.pittman@oregonstate.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/randallpittman/lt-autosnap',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.8,<4.0.0',
}


setup(**setup_kwargs)
