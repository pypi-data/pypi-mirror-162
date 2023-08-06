# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['omnihost']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['omnihost = omnihost.__main__:main']}

setup_kwargs = {
    'name': 'omnihost',
    'version': '0.2.0',
    'description': 'Easily convert native Gemini (gemtext markup) files into html and gophermaps for trihosting',
    'long_description': "# OMNIHOST\n\nA tool for those who would like to host native gemini content in parallel on the web as well as gopherspace.\n\n## Description\n\nEasily convert a directory full of gemtext markup into HTML and (eventually) gophermaps.\n\nThis tool is a work it progress. It should not be considered stable before the v1.0.0 release. Breaking changes may occur at any time.\n\nThere are still large swaths of functionality that have not been implemented, including but not limited to:\n - a reasonable deployment story\n - the ability to convert gemtext markup to gopher\n - logging\n - any sort of automated tests\n\nSee the Roadmap section for a complete list\n\n### Supported platforms\n\nThe current release has been manually tested on a linux machine. You should (probably) be alright if you have:\n * a new enough version of python or the ability to install one with `pyenv`\n * pip\n * [pyenv](https://github.com/pyenv/pyenv)\n * [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)\n\n### Dependencies\n\npython v3.10.5 or newer\n\nInstructions in the Installing section assume you are using `pyenv` and `pyenv-virtualenv`\n\n### Installing\n\nOmnihost can be installed from the python package index via pip ([pypi](https://pypi.org/project/omnihost))\n\nAs omnihost currently has no dependencies outside of the python standard library, you should be alright installing it in your global python environment if your system python is new enough. Best practice would be to install it in a virtual environment.\n\nInstall python v3.10.5 with `pyenv` if your system python uses a different version\n```\n$ pyenv install 3.10.5\n```\n\nCreate a virtual environment using `pyenv-virtualenv`\n```\npyenv virtualenv 3.10.5 omnihost\n```\n\n\nActivate the venv\n```\n$ pyenv activate omnihost\n```\n\nInstall omnihost in the virtual environment\n```\n$ python3 -m pip install omnihost\n```\n\n### Running\n\nActivate your venv\n```\n$ pyenv activate omnihost\n```\n\nRun omnihost\n```\n$ omnihost -i <gemtext/source/dir> -w <html/output/dir> -o <gemtext/output/dir> -g <gopher/output/dir> -s <stylesheet/path>\n```\n\nArguments:\n * `-i` gemtext source directory path. This argument is required.\n * `-w` html output directory path. This argument is optional. If an html output path is provided, gemtext files will be converted to html and placed in this directory. This directory must be empty.\n * `-o` gemini output directory path. This argument is optional. If a gemini output path is provided, gemtext files will be copied from the source directory to this directory.\n * `-g` gopher output directory path. This argument is optional. At present nothing is done with this argument. Eventually, if a gopher output path is provided, gemtext files will be converted to gophermaps and placed in this directory. This directory must be empty.\n * `-s` stylesheet path. This argument is optional. If a stylesheet path is provided, the stylesheet will be copied to \\<html/output/dir>/css/\\<stylesheet> and linked to the html pages as css/\\<stylesheet>\n \n ## Roadmap\n \n This is roughly ordered by priority except for conversion of gemtext to gophermaps. That's listed first because it's the biggest piece of missing functionality, but I'm planning to shore up the html conversion before adding that in\n \n  * Add ability to convert gemtext to gophermaps\n  * Add logging\n  * Improve error handling, add custom exception types\n  * Add automated tests\n  * Add support for nested directory structures for both input and output instead of requiring all input files to be in the top level of the input directory\n  * Improve formatting of html output to make it nicely human-readable\n  * Consider adding a preprocessing step using something like mdbook to allow for for meta control of generated pages. Would allow for things like:\n    + stylesheets specified per page\n    + titles that aren't dependent on the file name\n    + metadata to support things like auto-generation of subject indexes for wikis\n\n## License\n\nThis project is licensed under the MIT License - see the LICENSE.txt file for details",
    'author': 'Brett Gleason',
    'author_email': 'brettmgleason@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/b-src/omnihost',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
