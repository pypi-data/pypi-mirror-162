# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cmake_language_server']

package_data = \
{'': ['*']}

install_requires = \
['pygls>=0.12,<0.13']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=4.8,<5.0']}

entry_points = \
{'console_scripts': ['cmake-language-server = '
                     'cmake_language_server.server:main']}

setup_kwargs = {
    'name': 'cmake-language-server',
    'version': '0.1.6',
    'description': 'CMake LSP Implementation',
    'long_description': '# cmake-language-server\n[![PyPI](https://img.shields.io/pypi/v/cmake-language-server)](https://pypi.org/project/cmake-language-server)\n[![AUR version](https://img.shields.io/aur/version/cmake-language-server)](https://aur.archlinux.org/packages/cmake-language-server/)\n[![GitHub Actions (Tests)](https://github.com/regen100/cmake-language-server/workflows/Tests/badge.svg)](https://github.com/regen100/cmake-language-server/actions)\n[![codecov](https://codecov.io/gh/regen100/cmake-language-server/branch/master/graph/badge.svg)](https://codecov.io/gh/regen100/cmake-language-server)\n[![GitHub](https://img.shields.io/github/license/regen100/cmake-language-server)](https://github.com/regen100/cmake-language-server/blob/master/LICENSE)\n\nCMake LSP Implementation.\n\nAlpha Stage, work in progress.\n\n## Features\n- [x] Builtin command completion\n- [x] Documentation for commands and variables on hover\n- [x] Formatting (by [`cmake-format`](https://github.com/cheshirekow/cmake_format))\n\n## Commands\n\n- `cmake-language-server`: LSP server\n\n## Installation\n\n```bash\n$ pip install cmake-language-server\n```\n\n### Tested Clients\n\n- Neovim ([neoclide/coc.nvim][coc.nvim], [prabirshrestha/vim-lsp][vim-lsp])\n\n#### Neovim\n\n##### coc.nvim\n\n```jsonc\n  "languageserver": {\n    "cmake": {\n      "command": "cmake-language-server",\n      "filetypes": ["cmake"],\n      "rootPatterns": [\n        "build/"\n      ],\n      "initializationOptions": {\n        "buildDirectory": "build"\n      }\n    }\n  }\n```\n\n##### vim-lsp\n\n```vim\nif executable(\'cmake-language-server\')\n  au User lsp_setup call lsp#register_server({\n  \\ \'name\': \'cmake\',\n  \\ \'cmd\': {server_info->[\'cmake-language-server\']},\n  \\ \'root_uri\': {server_info->lsp#utils#path_to_uri(lsp#utils#find_nearest_parent_file_directory(lsp#utils#get_buffer_path(), \'build/\'))},\n  \\ \'whitelist\': [\'cmake\'],\n  \\ \'initialization_options\': {\n  \\   \'buildDirectory\': \'build\',\n  \\ }\n  \\})\nendif\n```\n\n### Configuration\n* `buildDirectory`\n  This language server uses CMake\'s file API to get cached variables.\n  The API communicates using `<buildDirectory>/.cmake/api/`.\n  `buildDirectory` is relative path to the root uri of the workspace.\n  To configure the build tree, you need to run the cmake command such as `cmake .. -DFOO=bar`.\n\n\n[coc.nvim]: https://github.com/neoclide/coc.nvim\n[vim-lsp]: https://github.com/prabirshrestha/vim-lsp\n',
    'author': 'regen',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/regen100/cmake-language-server',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
