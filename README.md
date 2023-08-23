# github-archive-repos

Archive all public repositories of any GitHub user.

```
usage: gh-archive.py [-h] -u <name> -d <dir>

options:
  -h, --help            show this help message and exit
  -u <name>, --user-name <name>
                        the github username
  -d <dir>, --dir <dir>
                        the directory to download the archives to
```

## Install

This small script uses only the Python standard library, no need for installation instructions.

You can use it like this:

```console
$ python gh-archive.py -u <USER_NAME> -d <ARCHIVES_DIR>
```

To add it to the PATH:

```
(echo '#!/usr/bin/env python' && cat gh-archive.py) > temp.py && mv temp.py gh-archive
chmod u+x gh-archive
mv gh-archive ~/.local/bin
```
