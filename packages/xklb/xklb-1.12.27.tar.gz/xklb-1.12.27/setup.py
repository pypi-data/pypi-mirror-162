# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xklb']

package_data = \
{'': ['*']}

install_requires = \
['catt>=0.12.9,<0.13.0',
 'ffmpeg-python>=0.2.0,<0.3.0',
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
    'version': '1.12.27',
    'description': 'xk library',
    'long_description': '# lb: opinionated media library\n\nA wise philosopher once told me, "[The future is [...] auto-tainment](https://www.youtube.com/watch?v=F9sZFrsjPp0)".\n\nRequires `ffmpeg`\n\n## Install\n\n    pip install xklb\n\n## Quick Start -- filesystem\n\n### 1. Extract Metadata\n\nFor the initial scan it takes about six hours to scan sixty terabytes. If you want to update the database run the same command again--any new files will be scanned and it is much, much quicker.\n\n    lb extract tv.db ./video/folder/\n    OR\n    lb extract ./tv/  # when not specified, db will be created as `video.db`\n    OR\n    lb extract --audio ./music/  # db will be created as `audio.db`\n\n### 2. Watch / Listen from local files\n\n    wt tv.db                       # the default post-action is to do nothing after playing\n    wt tv.db --post-action delete  # delete file after playing\n    lt boring.db --post-action=ask # ask to delete after playing\n\n## Quick Start -- virtual\n\n### 1. Download Metadata\n\nDownload playlist and channel metadata. Break free of the YouTube algo~\n\n    lb tubeadd educational.db https://www.youtube.com/c/BranchEducation/videos\n\nYou can add more than one at a time.\n\n    lb tubeadd maker.db https://www.youtube.com/c/CuriousMarc/videos https://www.youtube.com/c/element14presents/videos/ https://www.youtube.com/c/DIYPerks/videos\n\nAnd you can always add more later--even from different websites.\n\n    lb tubeadd maker.db https://vimeo.com/terburg\n\nTo prevent mistakes the default configuration is to download metadata for only the newest 20,000 videos per playlist/channel.\n\n    lb tubeadd maker.db --yt-dlp-config playlistend=1000\n\nBe aware that there are some YouTube Channels which have many items--for example the TEDx channel has about 180,000 videos. Some channels even have upwards of two million videos. More than you could likely watch in one sitting. On a high-speed connection (>500 Mbps), it can take up to five hours just to download the metadata for 180,000 videos. My advice: start with the 20,000.\n\n#### 1a. Get new videos for saved playlists\n\nTubeupdate will go through all added playlists and fetch metadata of any new videos not previously seen.\n\n    lb tubeupdate\n\nYou can also include your own yt-dlp download archive to skip downloaded videos and stop before scanning the full playlist.\n\n    lb tubeupdate --yt-dlp-config download_archive=rel/loc/archive.txt\n\n### 2. Watch / Listen from websites\n\n    lb tubewatch maker.db\n\nIf you like this I also have a [web version](https://unli.xyz/eject/)--but this Python version has more features and it can handle a lot more data.\n\n## Organize using separate databases\n\n    lb extract --audio both.db ./audiobooks/ ./podcasts/\n    lb extract --audio audiobooks.db ./audiobooks/\n    lb extract --audio podcasts.db ./podcasts/ ./another/more/secret/podcasts_folder/\n\n## Example Usage\n\n### Repeat\n\n    lt -u random         # listen to ONE random song\n    lt --limit 5         # listen to FIVE songs\n    lt -l inf            # listen to songs indefinitely\n    lt -s infinite       # listen to songs from the band infinite\n\nIf that\'s confusing (or if you are trying to load 4 billion files) you could always use your shell:\n\n    function repeat\n        while $argv\n            and :\n        end\n    end\n\n    repeat lt -s finite  # listen to finite songs infinitely\n\n### Watch longest videos\n\n    wt tv.db --sort duration desc\n\n### Watch specific video series in order\n\n    wt tv.db --search \'title of series\' --play-in-order\n\nThere are multiple strictness levels of --play-in-order. If things aren\'t playing in order try adding more `O`s\n\n    wt tv.db --search \'title of series\' -O    # default\n    wt tv.db --search \'title of series\' -OO   # slower, more complex algorithm\n    wt tv.db --search \'title of series\' -OOO  # most strict\n\n### Suggested Usage\n\n    lt -cast -cast-to \'Office pair\' -s \'  ost\'      # listen to OSTs on chromecast groups\n    wt -u priority -w sub=0  # for exercising and watching YouTube\n    wt -u duration --print -s \'video title\'  # check if you\'ve downloaded something before\n\n## Advanced Features\n\n### Extract\n\nIf you want to specify more than one directory you will need to make the db file explicit:\n\n    lb extract --filesystem fs.db one/ two/\n\n## Searching filesystem\n\nYou can also use `lb` for any files:\n\n    $ lb extract -fs ~/d/41_8bit/\n\n    $ lb fs fs.db -p a -s mario luigi\n    ╒═══════════╤══════════════╤══════════╤═════════╕\n    │ path      │   sparseness │ size     │   count │\n    ╞═══════════╪══════════════╪══════════╪═════════╡\n    │ Aggregate │            1 │ 215.0 MB │       7 │\n    ╘═══════════╧══════════════╧══════════╧═════════╛\n\n    $ lb fs -p -s mario -s luigi -s jpg -w is_dir=0 -u \'size desc\'\n    ╒═══════════════════════════════════════╤══════════════╤═════════╕\n    │ path                                  │   sparseness │ size    │\n    ╞═══════════════════════════════════════╪══════════════╪═════════╡\n    │ /mnt/d/41_8bit/roms/gba/media/images/ │      1.05632 │ 58.2 kB │\n    │ Mario & Luigi - Superstar Saga (USA,  │              │         │\n    │ Australia).jpg                        │              │         │\n    ├───────────────────────────────────────┼──────────────┼─────────┤\n    │ /mnt/d/41_8bit/roms/gba/media/box3d/M │      1.01583 │ 44.4 kB │\n    │ ario & Luigi - Superstar Saga (USA,   │              │         │\n    │ Australia).jpg                        │              │         │\n    ╘═══════════════════════════════════════╧══════════════╧═════════╛\n\n### TODO\n\n- all: Documentation\n- all: is_deleted column\n- all: how much watched statistics\n- all: split_by_silence without modifying files\n- all: Tests\n- tube: prevent adding duplicates\n- tube: Download subtitle to embed in db tags for search\n- tube: Playlists subcommand: view virtual aggregated pattens\n',
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
