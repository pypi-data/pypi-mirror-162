# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clock_cli']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=1.2.2,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'tabulate>=0.8.10,<0.9.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['clock = clock_cli:cli']}

setup_kwargs = {
    'name': 'clock-cli',
    'version': '0.1.4',
    'description': 'A command-line time zone converter',
    'long_description': '# Clock CLI\n\nA simple time zone converter for the command line. \n\n## Usage\n\nInput a time (flexibly parsed by [Arrow](https://arrow.readthedocs.io/en/latest/)) and\nsee the time localized in all your time zones. If a timezone is provided, the input time\nis parsed in that time zone. Otherwise, the input time is parsed in your local time.\n\n```\n$ clock "2022-08-10 22:00" -t "Asia/Hong_Kong"\nTime zone            Local time\n-------------------  -----------------------\nAmerica/New_York     2022-08-10 10:00 -04:00\nAmerica/Los_Angeles  2022-08-10 07:00 -07:00\nAsia/Hong_Kong       2022-08-10 22:00 +08:00\n```\n\nAdd a new time zone using `--add`. When the entered text matches multiple \n[IANA time zones](https://www.iana.org/time-zones), you will be prompted to choose\nwhich you want. \n\n```\n$ clock 2022 --add sin\nMultiple time zones matched \'sin\'. Which is correct?\n0. Europe/Chisinau\n1. Singapore\n2. Europe/Helsinki\n3. Europe/Busingen\n4. Asia/Singapore\n> :\n```\n\nClock CLI saves a list of output time zones in `~/.clock`; feel free to edit this list directly. \n\n```\n$ cat ~/.clock\ntimezones = [ "America/New_York", "America/Los_Angeles", "Asia/Hong_Kong", ]\n```\n\nAdditional options are provided for output formatting and debugging. \n\n```\n$ clock --help\nUsage: clock [OPTIONS] TIME\n\n  Shows a time in multiple time zones.\n\nOptions:\n  -t, --timezone TEXT  Time zone of input time\n  -f, --format TEXT    Output time format\n  -d, --debug          Show debug messages\n  --add TEXT           Add a time zone\n  --help               Show this message and exit.\n```\n\n## License\n\nCopyright 2022 Chris Proctor\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n',
    'author': 'Chris Proctor',
    'author_email': 'github.com@accounts.chrisproctor.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cproctor/clock',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
