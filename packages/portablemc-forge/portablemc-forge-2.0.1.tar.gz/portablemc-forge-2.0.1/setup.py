# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['portablemc_forge']

package_data = \
{'': ['*'],
 'portablemc_forge': ['wrapper/*',
                      'wrapper/src/main/java/argo/jdom/*',
                      'wrapper/src/main/java/com/google/common/base/*',
                      'wrapper/src/main/java/net/minecraftforge/installer/*',
                      'wrapper/src/main/java/net/minecraftforge/installer/actions/*',
                      'wrapper/src/main/java/net/minecraftforge/installer/json/*',
                      'wrapper/src/main/java/portablemc/wrapper/*',
                      'wrapper/target/*']}

install_requires = \
['portablemc>=3,<4']

setup_kwargs = {
    'name': 'portablemc-forge',
    'version': '2.0.1',
    'description': "Start Minecraft using the Forge mod loader using '<exec> start forge:[<mc-version>]'.",
    'long_description': '# Forge add-on\nThe forge add-on allows you to install and run Minecraft with forge mod loader in a single command \nline!\n\n![PyPI - Version](https://img.shields.io/pypi/v/portablemc-forge?label=PyPI%20version&style=flat-square) &nbsp;![PyPI - Downloads](https://img.shields.io/pypi/dm/portablemc-forge?label=PyPI%20downloads&style=flat-square)\n\n```console\npip install --user portablemc-forge\n```\n\n## Usage\nThis add-on extends the syntax accepted by the [start](/README.md#start-the-game) sub-command, by \nprepending the version with `forge:`. Almost all releases are supported by forge, the latest \nreleases are often supported, if not please refer to forge website. You can also append either\n`-recommended` or `-latest` to the version to take the corresponding version according to the\nforge public information, this is reflecting the "Download Latest" and "Download Recommended" on\nthe forge website. You can also use version aliases like `release` or equivalent empty version \n(just `forge:`). You can also give the exact forge version like `1.18.1-39.0.7`, in such cases,\nno HTTP request is made if the version is already installed.\n\n*Note that this add-on uses the same JVM used to start the game (see `--jvm` argument).*\n\n## Examples\n```sh\nportablemc start forge:               # Start recommended forge version for latest release\nportablemc start forge:release        # Same as above\nportablemc start forge:1.18.1         # Start recommended forge for 1.18.1\nportablemc start forge:1.18.1-39.0.7  # Start the exact forge version 1.18.1-39.0.7\nportablemc start --dry forge:         # Install (and exit) recommended forge version for latest release\n```\n\n## Credits\n- [Forge Website](https://files.minecraftforge.net/net/minecraftforge/forge/)\n- Consider supporting [LexManos](https://www.patreon.com/LexManos/)\n',
    'author': 'Théo Rozier',
    'author_email': 'contact@theorozier.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
