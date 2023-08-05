# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cf2tf', 'cf2tf.cloudformation', 'cf2tf.conversion', 'cf2tf.terraform']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'cfn-flip>=1.3.0,<2.0.0',
 'click-log>=0.4.0,<0.5.0',
 'click>=8.1.2,<9.0.0',
 'pytest>=7.1.2,<8.0.0',
 'requests>=2.27.1,<3.0.0',
 'thefuzz[speedup]>=0.19.0,<0.20.0']

entry_points = \
{'console_scripts': ['cf2tf = cf2tf.app:cli']}

setup_kwargs = {
    'name': 'cf2tf',
    'version': '0.2.6',
    'description': 'Convert Cloudformation Templates to Terraform.',
    'long_description': '<!-- PROJECT SHIELDS -->\n<!--\n*** I\'m using markdown "reference style" links for readability.\n*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).\n*** See the bottom of this document for the declaration of the reference variables\n*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.\n*** https://www.markdownguide.org/basic-syntax/#reference-style-links\n-->\n[![Python][python-shield]][pypi-url]\n[![Latest][version-shield]][pypi-url]\n[![Tests][test-shield]][test-url]\n[![Coverage][codecov-shield]][codecov-url]\n[![License][license-shield]][license-url]\n<!-- [![Contributors][contributors-shield]][contributors-url]\n[![Forks][forks-shield]][forks-url]\n[![Stargazers][stars-shield]][stars-url]\n[![Issues][issues-shield]][issues-url] -->\n\n<!-- PROJECT LOGO -->\n<br />\n<p align="center">\n  <!-- <a href="https://github.com/DontShaveTheYak/cf2tf">\n    <img src="images/logo.png" alt="Logo" width="80" height="80">\n  </a> -->\n\n  <h3 align="center">Cloudformation 2 Terraform</h3>\n\n  <p align="center">\n    Convert your Cloudformation templates to Terraform.\n    <!-- <br />\n    <a href="https://github.com/DontShaveTheYak/cf2tf"><strong>Explore the docs »</strong></a>\n    <br /> -->\n    <br />\n    <!-- <a href="https://github.com/DontShaveTheYak/cf2tf">View Demo</a>\n    · -->\n    <a href="https://github.com/DontShaveTheYak/cf2tf/issues">Report Bug</a>\n    ·\n    <a href="https://github.com/DontShaveTheYak/cf2tf/issues">Request Feature</a>\n    ·\n    <!-- <a href="https://la-tech.co/post/hypermodern-cloudformation/getting-started/">Guide</a> -->\n  </p>\n</p>\n\n\n\n<!-- TABLE OF CONTENTS -->\n<details open="open">\n  <summary>Table of Contents</summary>\n  <ol>\n    <li>\n      <a href="#about-the-project">About The Project</a>\n    </li>\n    <li>\n      <a href="#getting-started">Getting Started</a>\n      <ul>\n        <li><a href="#prerequisites">Prerequisites</a></li>\n        <li><a href="#installation">Installation</a></li>\n      </ul>\n    </li>\n    <li><a href="#usage">Usage</a></li>\n    <li><a href="#roadmap">Roadmap</a></li>\n    <li><a href="#contributing">Contributing</a></li>\n    <!-- <li><a href="#license">License</a></li> -->\n    <li><a href="#contact">Contact</a></li>\n    <li><a href="#acknowledgements">Acknowledgements</a></li>\n  </ol>\n</details>\n\n## About The Project\n\n<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->\n\n`cf2tf` is a CLI tool that attempts to convert Cloudformation to Terraform. We say attempt because it\'s not really possible to make the conversion with 100% accuracy (currently) because of several reasons mostly around converting a Map value in Cloudformation to the [correct value in HCL](https://github.com/hashicorp/hcl/issues/294#issuecomment-446388342).\n\n## Getting Started\n\n### Prerequisites\n\nCloud-Radar requires python >= 3.7\n\n### Installation\n\ncf2tf is available as an easy to install pip package.\n```sh\npip install cf2tf\n```\n\n## Usage\n\nTo convert a template to terraform.\n```sh\ncf2tf my_template.yaml\n```\n\nThis above command will dump all the terraform resources to stdout. You might want to save the results:\n```sh\ncf2tf my_template.yaml > main.tf\n```\n\nIf you prefer to have each resource in its own file then:\n```sh\ncf2tf my_template.yaml -o some_dir\n```\nIf `some_dir` doesn\'t exist, then it will be created for you. Then each resource type will be saved to a specific file (variables.tf, outputs.tf etc.).\n\n## Roadmap\n\n- Better conversion of Cloudformation Maps to Terraform (Maps, Block and json)\n- Allow overides for specific resources\n- Handle more advanced Cloudformation parameter types like SSM/Secrets manager\n- Better handling of Recources/Properties that failed conversion\n- Only download files needed, not entire terraform source code (200MB)\n\nSee the [open issues](https://github.com/DontShaveTheYak/cf2tf/issues) for a list of proposed features (and known issues).\n\n## Contributing\n\nContributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.\n\n\n\nThis project uses poetry to manage dependencies and pre-commit to run formatting, linting and tests. You will need to have both installed to your system as well as python 3.9.\n\n1. Fork the Project\n2. Setup the environment.  \n   This project uses vscode devcontainer to provide a completly configured development environment. If you are using vscode and have the remote container extension installed, you should be asked to use the devcontainer when you open this project inside of vscode.\n\n   If you are not using devcontainers then you will need to have python installed. Install the `poetry`, `nox`, `nox_poetry` and `pre-commit` packages. Then run `poetry install` and `pre-commit install` commands. \n\n   Most of the steps can be found in the [Dockerfile](.devcontainer/Dockerfile).\n2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)\n3. Commit your Changes (`git commit -m \'Add some AmazingFeature\'`)\n4. Push to the Branch (`git push origin feature/AmazingFeature`)\n5. Open a Pull Request\n\n<!-- ## License\n\nDistributed under the Apache-2.0 License. See [LICENSE.txt](./LICENSE.txt) for more information. -->\n\n## Contact\n\nLevi - [@shady_cuz](https://twitter.com/shady_cuz)\n\n<!-- ACKNOWLEDGEMENTS -->\n## Acknowledgements\n* [Cloud-Radar](https://github.com/DontShaveTheYak/cloud-radar) - A unit/functional testing framework for Cloudformation templates.\n* [cfn_tools from cfn-flip](https://github.com/awslabs/aws-cfn-template-flip) - Used to convert template from yml to python dict.\n* [Best-README-Template](https://github.com/othneildrew/Best-README-Template) - The name says it all.\n\n<!-- MARKDOWN LINKS & IMAGES -->\n<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->\n[python-shield]: https://img.shields.io/pypi/pyversions/cf2tf?style=for-the-badge\n[version-shield]: https://img.shields.io/pypi/v/cf2tf?label=latest&style=for-the-badge\n[pypi-url]: https://pypi.org/project/cf2tf/\n[test-shield]: https://img.shields.io/github/workflow/status/DontShaveTheYak/cf2tf/Tests?label=Tests&style=for-the-badge\n[test-url]: https://github.com/DontShaveTheYak/cf2tf/actions?query=workflow%3ATests+branch%3Amaster\n[codecov-shield]: https://img.shields.io/codecov/c/gh/DontShaveTheYak/cf2tf/master?color=green&style=for-the-badge&token=bfF18q99Fl\n[codecov-url]: https://codecov.io/gh/DontShaveTheYak/cf2tf\n[contributors-shield]: https://img.shields.io/github/contributors/DontShaveTheYak/cf2tf.svg?style=for-the-badge\n[contributors-url]: https://github.com/DontShaveTheYak/cf2tf/graphs/contributors\n[forks-shield]: https://img.shields.io/github/forks/DontShaveTheYak/cf2tf.svg?style=for-the-badge\n[forks-url]: https://github.com/DontShaveTheYak/cf2tf/network/members\n[stars-shield]: https://img.shields.io/github/stars/DontShaveTheYak/cf2tf.svg?style=for-the-badge\n[stars-url]: https://github.com/DontShaveTheYak/cf2tf/stargazers\n[issues-shield]: https://img.shields.io/github/issues/DontShaveTheYak/cf2tf.svg?style=for-the-badge\n[issues-url]: https://github.com/DontShaveTheYak/cf2tf/issues\n[license-shield]: https://img.shields.io/github/license/DontShaveTheYak/cf2tf.svg?style=for-the-badge\n[license-url]: https://github.com/DontShaveTheYak/cf2tf/blob/master/LICENSE.txt\n[product-screenshot]: images/screenshot.png\n',
    'author': 'Levi Blaney',
    'author_email': 'shadycuz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DontShaveTheYak/cf2tf',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
