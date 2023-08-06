# Glartifacts
Python utility to analyze and clean up GitLab artifacts.

Glartifacts is a tool designed to help GitLab administrators manage CI job
artifacts. The artifact expiration functionality provided by GitLab (11.6, as
of this writing) is primitive. The goal of this project is to design and
implement improved artifact expiration policies which act as a model for 
future GitLab improvements.

See the [documentation](https://glartifacts.readthedocs.io/) for more detail on
how glartifacts works and how to use it.

## Requirements
Glartifacts requires Python 3.

It is also a tool for GitLab administrators, designed to run as root on the 
GitLab server. It connects directly to the GitLab database and Gitaly gRPC
service.

## Warning: Backup your database and artifacts
Be sure you have a GitLab backup before you start.

Glartifacts modifies the `ci_builds.artifacts_expire_at` column in the GitLab
database. The next execution of the `Sidekiq` background task will **remove**
CI artifacts from the database and file system. Once removed, artifacts
are non-recoverable.

## Installation
Glartifacts from PyPI using pip.
```
$ sudo pip install glartifacts
```

## Configuration
Glartifacts requires access to the GitLab database and Gitaly server. The 
default connection settings are based on a standard Omnibus install, but can be
modified for custom deployments via settings in `glartifacts.conf`. You can
also override individual settings per-invocation using environment variables.

The table below lists the available configuration options:

|Section   |Option   |ENV var   |Default |
|----------|---------|----------|--------|
|postgres |dbname |`GLARTIFACTS_DBNAME` |`gitlabhq_production` |
|postgres |user |`GLARTIFACTS_DBUSER` |`gitlab` |
|postgres |host |`GLARTIFACTS_DBHOST` |`/var/opt/gitlab/postgresql` |
|postgres |port |`GLARTIFACTS_DBPORT` |`5432` |
|gitaly |address |`GLARTIFACTS_GITALYADDR` |`unix:/var/opt/gitlab/gitaly/gitaly.socket` |

The following paths are searched for the glartifacts.conf. Settings are merged
for each conf file found: `Defaults` > `System Settings` > `User Settings`.
```
$HOME/.config/glartifacts/glartifacts.conf
/etc/glartifacts/glartifacts.conf
```
