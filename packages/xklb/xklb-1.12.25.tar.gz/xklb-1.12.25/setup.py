# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xklb']

package_data = \
{'': ['*']}

install_requires = \
['catt>=0.12.9,<0.13.0',
 'humanize>=4.2.3,<5.0.0',
 'ipython>=8.4.0,<9.0.0',
 'joblib>=1.1.0,<2.0.0',
 'mutagen>=1.45.1,<2.0.0',
 'natsort>=8.1.0,<9.0.0',
 'pandas>=1.4.3,<2.0.0',
 'protobuf<4',
 'rich>=12.5.1,<13.0.0',
 'sqlite-utils>=3.28,<4.0',
 'subliminal>=2.1.0,<3.0.0',
 'tabulate>=0.8.10,<0.9.0',
 'tinytag>=1.8.1,<2.0.0',
 'trash-cli>=0.22.4,<0.23.0']

entry_points = \
{'console_scripts': ['lb = xklb.lb:main',
                     'lt = xklb.lb:listen',
                     'wt = xklb.lb:watch']}

setup_kwargs = {
    'name': 'xklb',
    'version': '1.12.25',
    'description': 'xk library',
    'long_description': "## lb: opinionated media library\n\nRequires ffmpeg\n\n### Install\n\n```\npip install xklb\n```\n\n### Quick Start\n\n#### Step 1. Extract Metadata\n\n    lb extract tv.db ./video/folder/\n\n    lb extract --audio podcasts.db ./your/music/or/podcasts/folder/\n\n#### Step 2. Watch / Listen\n\n    wt tv.db  # the default post-action is to do nothing after viewing\n\n    wt --post-action delete tv.db  # delete file after viewing\n\n    lt --post-action=ask podcasts.db  # ask to delete or not after each file\n\n\n### Repeat!\n\n    lt -u random         # listen to ONE random song\n    lt --repeat 5        # listen to FIVE songs\n    lt -l inf            # listen to songs indefinitely\n    lt -s infinite       # listen to songs from the band infinite\n\nIf that's confusing you could always use your shell:\n\n```fish\nfunction repeat\n    while $argv\n        and :\n    end\nend\n\nrepeat lt -s finite  # listen to finite songs infinitely\n```\n\n### Example Usage\n\n\n#### Watch longest videos\n\n    wt tv.db --sort duration desc\n\n#### Watch specific video series in order\n\n    wt tv.db --search 'title of series' --play-in-order\n\n#### There are multiple strictness levels of --play-in-order. If things aren't playing in order try adding more `O`s:\n\n    wt tv.db --search 'title of series' -O    # default\n    wt tv.db --search 'title of series' -OO   # slower, more complex algorithm\n    wt tv.db --search 'title of series' -OOO  # most strict\n\n#### I usually use the following:\n\n    lt -cast -s '  ost'      # for listening to OSTs on my chromecast groups\n    wt -u priority -w sub=0  # for exercising and watching YouTube\n    wt -u duration --print -s 'video title'  # when I want to check if I've downloaded something before\n\n### Advanced Features\n\nIf you want to specify more than one directory you will need to make the db file explicit:\n\n    $ lb extract --filesystem fs.db one/ two/\n\n\n### Searching filesystem\n\nYou can also use `lb` for any files:\n\n    $ lb extract -fs ~/d/41_8bit/\n\n    $ lb fs fs.db -p a -s mario luigi\n    ╒═══════════╤══════════════╤══════════╤═════════╕\n    │ path      │   sparseness │ size     │   count │\n    ╞═══════════╪══════════════╪══════════╪═════════╡\n    │ Aggregate │            1 │ 215.0 MB │       7 │\n    ╘═══════════╧══════════════╧══════════╧═════════╛\n\n    $ lb fs -p -s mario -s luigi -s jpg -w is_dir=0 -u 'size desc'\n    ╒═══════════════════════════════════════╤══════════════╤═════════╕\n    │ path                                  │   sparseness │ size    │\n    ╞═══════════════════════════════════════╪══════════════╪═════════╡\n    │ /mnt/d/41_8bit/roms/gba/media/images/ │      1.05632 │ 58.2 kB │\n    │ Mario & Luigi - Superstar Saga (USA,  │              │         │\n    │ Australia).jpg                        │              │         │\n    ├───────────────────────────────────────┼──────────────┼─────────┤\n    │ /mnt/d/41_8bit/roms/gba/media/box3d/M │      1.01583 │ 44.4 kB │\n    │ ario & Luigi - Superstar Saga (USA,   │              │         │\n    │ Australia).jpg                        │              │         │\n    ╘═══════════════════════════════════════╧══════════════╧═════════╛\n",
    'author': 'Jacob Chapman',
    'author_email': '7908073+chapmanjacobd@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
