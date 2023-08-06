# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['minato', 'minato.commands', 'minato.common', 'minato.filesystems']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.0.0,<3.0.0']

extras_require = \
{'all': ['boto3>=1.0.0,<2.0.0', 'google-cloud-storage>=1.0.0,<2.0.0'],
 'gcs': ['google-cloud-storage>=1.0.0,<2.0.0'],
 's3': ['boto3>=1.0.0,<2.0.0']}

entry_points = \
{'console_scripts': ['minato = minato.__main__:run']}

setup_kwargs = {
    'name': 'minato',
    'version': '0.10.0',
    'description': 'Cached file system for online resources',
    'long_description': 'Minato\n======\n\n[![Actions Status](https://github.com/altescy/minato/workflows/CI/badge.svg)](https://github.com/altescy/minato/actions/workflows/ci.yml)\n[![Python version](https://img.shields.io/pypi/pyversions/minato)](https://github.com/altescy/minato)\n[![License](https://img.shields.io/github/license/altescy/minato)](https://github.com/altescy/minato/blob/master/LICENSE)\n[![pypi version](https://img.shields.io/pypi/v/minato)](https://pypi.org/project/minato/)\n\nCache & file system for online resources in Python\n\n\n## Features\n\nMinato enables you to:\n- Download & cache online recsources\n  - minato supports the following protocols: HTTP(S) / AWS S3 / Google Cloud Storage\n  - You can manage cached files via command line interface\n- Automatically update cached files based on ETag\n  - minato downloads new versions if available when you access cached files\n- Open online files super easily\n  - By using `minato.open`, you can read/write online resources like the built-in `open` method\n\n## Installation\n\n```\npip install minato[all]\n```\n\n## Usage\n\n### Python\n\n```python\nimport minato\n\n# Read / write files on online storage\nwith minato.open("s3://your_bucket/path/to/file", "w") as f:\n    f.write("Create a new file on AWS S3!")\n\n# Cache & manage online resources in local storage\nlocal_filename = minato.cached_path("http://example.com/path/to/archive.zip!inner/path/to/file")\n```\n\n### CLI\n\n```\n❯ poetry run minato --help\nusage: minato\n\npositional arguments:\n  {cache,list,remove,update}\n    cache               cache remote file and return cached local file path\n    list                show list of cached files\n    remove              remove cached files\n    update              update cached files\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --version             show program\'s version number and exit\n```\n',
    'author': 'Yasuhiro Yamaguchi',
    'author_email': 'altescy@fastmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/altescy/minato',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
