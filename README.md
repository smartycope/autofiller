# autofiller

A small popup to input various random data for you.

There's 2 options to use this. By default, the popup opens as soon as you run the program, so adding "python -m autofiller" as a global short works great.

You can also run "python -m autofiller -d &" to have it run in the background, detect when you press the keyboard shortcut, and open the window.

You can also customize the keyboard shortcut like this:
```bash
python -m autofiller -d -m meta -k r
# or
python -m autofiller --deamon --modifier ctrl --key 5
# or
python -m autofiller -d -m none -k f3
```

[![PyPI - Version](https://img.shields.io/pypi/v/autofiller.svg)](https://pypi.org/project/autofiller)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/autofiller.svg)](https://pypi.org/project/autofiller)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation
Note that, due to one of the dependancies, clang needs to be installed on your system:
```bash
sudo apt-get install clang
sudo dnf install clang
# ...etc
```
Then you can install the library itself:
```console
pip install autofiller
```

## License

`autofiller` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
