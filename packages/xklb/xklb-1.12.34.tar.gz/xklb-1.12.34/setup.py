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
                     'tl = xklb.lb:tubelisten',
                     'tw = xklb.lb:tubewatch',
                     'wt = xklb.lb:watch']}

setup_kwargs = {
    'name': 'xklb',
    'version': '1.12.34',
    'description': 'xk library',
    'long_description': '# lb: opinionated media library\n\nA wise philosopher once told me, "[The future is [...] auto-tainment](https://www.youtube.com/watch?v=F9sZFrsjPp0)".\n\nRequires `ffmpeg`\n\n## Install\n\n    pip install xklb\n\n## Quick Start -- filesystem\n\n### 1. Extract Metadata\n\nFor thirty terabytes of video the initial scan takes about four hours to complete. After that, rescans of the same path (or any subpaths) are much quicker--only new files will be read by `ffprobe`.\n\n    lb extract tv.db ./video/folder/\n\n### 2. Watch / Listen from local files\n\n    wt tv.db                          # the default post-action is to do nothing after playing\n    wt tv.db --post-action delete     # delete file after playing\n    lt finalists.db --post-action=ask # ask to delete after playing\n\n## Quick Start -- virtual\n\n### 1. Download Metadata\n\nDownload playlist and channel metadata. Break free of the YouTube algo~\n\n    lb tubeadd educational.db https://www.youtube.com/c/BranchEducation/videos\n\nYou can add more than one at a time.\n\n    lb tubeadd maker.db https://www.youtube.com/c/CuriousMarc/videos https://www.youtube.com/c/element14presents/videos/ https://www.youtube.com/c/DIYPerks/videos\n\nAnd you can always add more later--even from different websites.\n\n    lb tubeadd maker.db https://vimeo.com/terburg\n\nTo prevent mistakes the default configuration is to download metadata for only the newest 20,000 videos per playlist/channel.\n\n    lb tubeadd maker.db --yt-dlp-config playlistend=1000\n\nBe aware that there are some YouTube Channels which have many items--for example the TEDx channel has about 180,000 videos. Some channels even have upwards of two million videos. More than you could likely watch in one sitting. On a high-speed connection (>500 Mbps), it can take up to five hours just to download the metadata for 180,000 videos. My advice: start with the 20,000.\n\n#### 1a. Get new videos for saved playlists\n\nTubeupdate will go through all added playlists and fetch metadata of any new videos not previously seen.\n\n    lb tubeupdate\n\nYou can also include your own yt-dlp download archive to skip downloaded videos and speed up playlist scanning.\n\n    lb tubeupdate --yt-dlp-config download_archive=rel/loc/archive.txt\n\n### 2. Watch / Listen from websites\n\n    lb tubewatch maker.db\n\nIf you like this I also have a [web version](https://unli.xyz/eject/)--but this Python version has more features and it can handle a lot more data.\n\n## Things to know\n\nWhen the database file path is not specified, `video.db` will be created / used.\n\n    lb extract ./tv/\n\nThe same for audio: `audio.db` will be created / used.\n\n    lb extract --audio ./music/\n\nLikewise, `fs.db` from:\n\n    lb extract --filesystem /any/path/\n\nIf you want to specify more than one directory you need to mention the db file explicitly.\n\n    lb extract --filesystem one/\n    lb extract --filesystem fs.db one/ two/\n\nOrganize via separate databases.\n\n    lb extract --audio both.db ./audiobooks/ ./podcasts/\n    lb extract --audio audiobooks.db ./audiobooks/\n    lb extract --audio podcasts.db ./podcasts/ ./another/more/secret/podcasts_folder/\n\n## Usage\n\n### Repeat\n\n    lt                  # listen to 120 random songs (DEFAULT_PLAY_QUEUE)\n    lt --limit 5        # listen to FIVE songs\n    lt -l inf -u random # listen to random songs indefinitely\n    lt -s infinite      # listen to songs from the band infinite\n\n### Watch longest videos\n\n    wt tv.db --sort duration desc\n\n### Watch specific video series in order\n\n    wt tv.db --search \'title of series\' --play-in-order\n\nThere are multiple strictness levels of --play-in-order. If things aren\'t playing in order try adding more `O`s\n\n    wt tv.db --search \'title of series\' -O    # default\n    wt tv.db --search \'title of series\' -OO   # slower, more complex algorithm\n    wt tv.db --search \'title of series\' -OOO  # most strict\n\n### See how many corrupt videos you have\n\n    lb wt -w \'duration is null\' -p a\n\n### Listen to OSTs on chromecast groups\n\n    lt -cast -cast-to \'Office pair\' -s \'  ost\'\n\n### Exercise and watch TV that doesn\'t have subtitles\n\n    wt -u priority -w sub=0\n\n### Check if you\'ve downloaded something before\n\n    wt -u duration --print -s \'video title\'\n\n### View how much time you have listened to music\n\n    lb lt -w play_count\'>\'0 -p a\n\n### See how much video you have\n\n    lb wt video.db -p a\n    ╒═══════════╤═════════╤═════════╤═════════╕\n    │ path      │   hours │ size    │   count │\n    ╞═══════════╪═════════╪═════════╪═════════╡\n    │ Aggregate │  145769 │ 37.6 TB │  439939 │\n    ╘═══════════╧═════════╧═════════╧═════════╛\n    Total duration: 16 years, 7 months, 19 days, 17 hours and 25 minutes\n\n### Search the filesystem\n\nYou can also use `lb` for any files:\n\n    $ lb extract -fs ~/d/41_8bit/\n\n    $ lb fs fs.db -p a -s mario luigi\n    ╒═══════════╤══════════════╤══════════╤═════════╕\n    │ path      │   sparseness │ size     │   count │\n    ╞═══════════╪══════════════╪══════════╪═════════╡\n    │ Aggregate │            1 │ 215.0 MB │       7 │\n    ╘═══════════╧══════════════╧══════════╧═════════╛\n\n    $ lb fs -p -s mario -s luigi -s jpg -w is_dir=0 -u \'size desc\'\n    ╒═══════════════════════════════════════╤══════════════╤═════════╕\n    │ path                                  │   sparseness │ size    │\n    ╞═══════════════════════════════════════╪══════════════╪═════════╡\n    │ /mnt/d/41_8bit/roms/gba/media/images/ │      1.05632 │ 58.2 kB │\n    │ Mario & Luigi - Superstar Saga (USA,  │              │         │\n    │ Australia).jpg                        │              │         │\n    ├───────────────────────────────────────┼──────────────┼─────────┤\n    │ /mnt/d/41_8bit/roms/gba/media/box3d/M │      1.01583 │ 44.4 kB │\n    │ ario & Luigi - Superstar Saga (USA,   │              │         │\n    │ Australia).jpg                        │              │         │\n    ╘═══════════════════════════════════════╧══════════════╧═════════╛\n\n### TODO\n\n- all: Tests\n- tube: postprocessor_hook\n- tube: None instead of nan\n- tube: prevent adding duplicates\n- tube: sqlite-utils\n- tube: Download subtitle to embed in db tags for search\n- tube: Documentation\n- fs: split_by_silence without modifying files\n- fs: is_deleted\n',
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
