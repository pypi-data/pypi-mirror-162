# lt-autosnap

## DISCLAIMER

Due to the following factors:

- This software is intended to be run with root privileges
- This software manages logical volumes on your machine, including creationg and deletion of snapshots
- There may be bugs in this software

...be advised that this software has the ability to at the least cause you **DATA LOSS** and at the worst
**SEVERELY DAMAGE OR IMPAIR** your operating system. **THIS IS NOT BACKUP SOFTWARE**.

See [LICENSE.txt](LICENSE.txt) for further disclaimers.

## Changelog

[See CHANGELOG.md](CHANGELOG.md)

## Introduction

The purpose of this tool is to automate management of LVM thin pool snapshots. It is intended to be used with
cron or systemd timers for scheduling.

[There is a guide on the Samba
website](https://wiki.samba.org/index.php/Rotating_LVM_snapshots_for_shadow_copy) for setting up rotating LVM
snapshots for use with Samba's implementation of Volume Shadow Copy. This script is based on the Bash script
in that guide. It can mount snapshots to a specified path with dirnames compatible with Volume Shadow Copy,
e.g. `@GMT-2022.04.28-22.35.17`. For more on setting up Samba for shadow copies, see
[https://www.samba.org/samba/docs/current/man-html/vfs_shadow_copy2.8.html](https://www.samba.org/samba/docs/current/man-html/vfs_shadow_copy2.8.html)

## Requirements

This tool requires Python 3.6 or later. For recent Linux distributions the system Python interpreter should
suffice. `pip` or `pip3` is required for installation, so you may need to install `python3-pip` or similar
package.

### Python Dependencies

Since I expect this to be a system package, I tried to minimize the dependencies it would install.

- If you are using Python 3.6, pip will install the `dataclasses` backport for 3.6.
- pip will install `single-version` for package version management.

## Installation

This is a rare case of installing something with Python's `pip` as root.

```bash
sudo pip install lt-autosnap
# --or--
sudo pip3 install lt-autosnap
```

## Configuration

Create a config file with `ltautosnap genconf > ltautosnap.conf`. The comments provide guidance on how to
configure volumes and snap sets. Modify the config file with the details about your volumes and desired snap
set and, as root, copy it to `/etc/ltautosnap.conf`.

## Usage

Most commands require root privileges, even `list`, since it runs `lvs` which usually requires root.

- Run `ltautosnap -h` for a list of all commands.
- As root, create a crontab file at `/etc/cron.d/ltautosnap` to generate snaps.

   Examples:

   ```bash
   # If desired, set an email address to send error messages
   #   Cron will usually email stdout and stderr if you have mail set up with
   #   Postfix or similar MTA.
   MAILTO=example@example.org

   # Generate a snapshot for vol0, set0 every day at midnight, no matter what
   0 0 * * *  root ltautosnap snap 0 0

   # Every hour at 3 minutes after the hour, for vol0, set1, if a period has
   #   elapsed since the last snap of the set, create another one.
   3 * * * *  root ltautosnap autosnap 0 1

   # Every day at 3 AM remove all extra snaps (beyond each snapset's count)
   #   starting with the oldest
   0 3 * * *  root ltautosnap clean all

   # Every hour at 5 after, for volume 1, automatically create new snaps as needed
   #   and clean old ones for all snap sets.
   5 0 * * *  root ltautosnap autosnap 1 --autoclean

   # Every day at noon, check if each volume's pool has exceeded the warning level
   #   This will log a warning to stderr if the warning level has been exceeded.
   #   If MAILTO is set and your MTA is configured, you'll be emailed only if the
   #   warning percent is exceeded.
   0 12 * * *  root ltautosnap check all

   # On the first day of the month, do the same but print the % used space to
   #   stderr no matter what. If MAILTO is set and your MTA is configued, you'll
   #   be emailed the volume usage every month.
   0 0 1 * *  root ltautosnap check all -v
   ```
