# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scri',
 'scri.LVC',
 'scri.SpEC',
 'scri.SpEC.file_io',
 'scri.asymptotic_bondi_data',
 'scri.pn']

package_data = \
{'': ['*'], 'scri.SpEC': ['samples/*']}

install_requires = \
['h5py>=3,<4',
 'numba>=0.55',
 'numpy-quaternion>=2022.4',
 'numpy>=1.20',
 'scipy>=1.0,<2.0',
 'spherical-functions>=2022.4',
 'spinsfast>=2022.4',
 'sxs>=2022.3.4',
 'tqdm>=4.48.2,<4.61.2']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0'],
 'mkdocs': ['mkdocs>=1.1.2,<2.0.0'],
 'mktheapidocs': ['mktheapidocs[plugin]>=0.2.0,<0.3.0']}

setup_kwargs = {
    'name': 'scri',
    'version': '2022.8.0',
    'description': 'Time-dependent functions of spin-weighted spherical harmonics',
    'long_description': '[![Test and deploy](https://github.com/moble/scri/actions/workflows/build.yml/badge.svg)](https://github.com/moble/scri/actions/workflows/build.yml)\n[![Documentation Status](https://readthedocs.org/projects/scri/badge/?version=latest)](https://scri.readthedocs.io/en/latest/?badge=latest)\n[![PyPI Version](https://img.shields.io/pypi/v/scri?color=)](https://pypi.org/project/scri/)\n[![Conda Version](https://img.shields.io/conda/vn/conda-forge/scri.svg?color=)](https://anaconda.org/conda-forge/scri)\n[![MIT License](https://img.shields.io/github/license/moble/scri.svg)](https://github.com/moble/scri/blob/main/LICENSE)\n[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.4041971.svg)](https://doi.org/10.5281/zenodo.4041971)\n\nScri\n====\n\nPython/numba code for manipulating time-dependent functions of spin-weighted\nspherical harmonics\n\n## Citing this code\n\nIf you use this code for academic work (I can\'t actually imagine any other use\nfor it), please cite the latest version that you used in your publication. The DOI is:\n\n* DOI: [10.5281/zenodo.4041972](https://doi.org/10.5281/zenodo.4041972) ([BibTeX entry on Zenodo](https://zenodo.org/record/4041972/export/hx#.YFNpLe1KiV4))\n\nAlso please cite the papers for/by which it was produced:\n\n* "Angular velocity of gravitational radiation from precessing binaries and the\n  corotating frame", Boyle,\n  [Phys. Rev. D, 87, 104006](http://link.aps.org/doi/10.1103/PhysRevD.87.104006)\n  (2013).\n* "Gravitational-wave modes from precessing black-hole binaries", Boyle *et\n  al.*, http://arxiv.org/abs/1409.4431 (2014).\n* "Transformations of asymptotic gravitational-wave data", Boyle,\n  [Phys. Rev. D, 93, 084031](http://link.aps.org/doi/10.1103/PhysRevD.93.084031)\n  (2015).\n\nBibtex entries for these articles can be found\n[here](https://raw.githubusercontent.com/moble/scri/master/scri.bib).  It might\nalso be nice of you to provide a link directly to this source code.\n\n\n## Quick start\n\nAssuming you have the [`anaconda`](http://continuum.io/downloads) distribution\nof python (the preferred distribution for scientific applications),\ninstallation is as simple as\n\n```sh\nconda update -y --all\nconda install -c conda-forge scri\n```\n\nIf you need to install `anaconda` first, it\'s very easy and doesn\'t require root permissions.  Just [download](http://continuum.io/downloads) and follow the instructions — particularly setting your `PATH`.  Also, make sure `PYTHONPATH` and `PYTHONHOME` are *not* set.  Ensure that it worked by running `python --version`.  It should say something about anaconda; if not, you probably forgot to set your `PATH`.  Now just run the installation command above.\n\nThen, in python, you can check to make sure installation worked with\n\n```python\nimport scri\nw = scri.WaveformModes()\n```\n\nNow, `w` is an object to contain time and waveform data, as well as various\nrelated pieces of information -- though it is trivial in this case, because we\nhaven\'t given it any data.  For more information, see the docstrings of `scri`,\n`scri.WaveformModes`, etc.\n\n\n## Dependencies\n\nThe dependencies should be taken care of automatically by the quick\ninstallation instructions above.  However, if you run into problems (or if you\nfoolishly decide not to use anaconda to install things), it may be because you\nare missing some or all of these:\n\n  * Standard packages (come with full anaconda installation)\n    * [`numpy`](http://www.numpy.org/)\n    * [`scipy`](http://scipy.org/)\n    * [`matplotlib`](http://matplotlib.org/)\n    * [`h5py`](http://www.h5py.org/)\n    * [`numba`](http://numba.pydata.org/)\n  * My packages, available from anaconda.org and/or github\n    * [`fftw`](https://github.com/moble/fftw) (not actually mine,\n      but I maintain a copy for easy installation)\n    * [`spinsfast`](https://github.com/moble/spinsfast) (not actually mine,\n      but I maintain a copy with updated python features)\n    * [`quaternion`](https://github.com/moble/quaternion)\n    * [`spherical_functions`](https://github.com/moble/spherical_functions)\n\nAll these dependencies are installed automatically when you use the `conda`\ncommand described above.  The `anaconda` distribution can co-exist with your\nsystem python with no trouble -- you simply add the path to anaconda before\nyour system executables.  In fact, your system python probably needs to stay\ncrusty and old so that your system doesn\'t break, while you want to use a newer\nversion of python to actually run fancy new code like this.  This is what\n`anaconda` does for you.  It installs into your home directory, so it doesn\'t\nrequire root access.  It can be uninstalled easily, since it exists entirely\ninside its own directory.  And updates are trivial.\n\n### "Manual" installation\n\nThe instructions in the "Quick Start" section above should be sufficient, as\nthere really is no good reason not to use `anaconda`.  You will occasionally\nhear people complain about it not working; these people have not installed it\ncorrectly, and have other python-related environment variables that shouldn\'t\nbe there.  You don\'t want to be one of those people.\n\nNonetheless, it is possible to install these packages without anaconda -- in\nprinciple.  The main hurdle to overcome is `numba`.  Maybe there are nice ways\nto install `numba` without `anaconda`.  I don\'t know.  I don\'t care.  But if\nyou\'re awesome enough to do that, you\'re awesome enough to install all the\nother dependencies without advice from me.  But in short, you can either use\nthe `setup.py` files as usual, or just use `pip`:\n\n```sh\npip install git+git://github.com/moble/spinsfast\npip install git+git://github.com/moble/quaternion\npip install git+git://github.com/moble/spherical_functions\npip install git+git://github.com/moble/scri\n```\n\nAnd since you\'re just *soooo* cool, you already know that the `--user` flag is\nmissing from those commands because you\'re presumably using a virtual\nenvironment, hotshot.\n\n(If you\'re really not that cool, and aren\'t using `virtualenv`, you might think\nyou should `sudo` those commands.  But there\'s no need if you just use the\n`--user` flag instead.  That installs packages into your user directory, which\nis usually a better idea.)\n\nNote that `spinsfast` depends (for both building and running) on `fftw`.  If\nyou run into build problems with `spinsfast`, it probably can\'t find the\nheader or library for `fftw`.  See the documentation of my copy of `spinsfast`\n[here](https://github.com/moble/spinsfast#manual-installation) for suggestions\non solving that problem.  Of course, with `conda`, `fftw` is installed in the\nright place from my channel automatically.\n\n\n## Documentation\n\nTutorials and automatically generated API documentation are available on [Read the Docs: scri](https://scri.readthedocs.io/).\n\n## Acknowledgments\n\nThis code is, of course, hosted on github; because it is an open-source\nproject, the hosting is free, and all the wonderful features of github are\navailable, including free wiki space and web page hosting, pull requests, a\nnice interface to the git logs, etc.\n\nEvery change in this code is\n[auomatically tested](https://travis-ci.org/moble/scri) on\n[Travis-CI](https://travis-ci.org/).  This is a free service (for open-source\nprojects like this one), which integrates beautifully with github, detecting\neach commit and automatically re-running the tests.  The code is downloaded and\ninstalled fresh each time, and then tested, on both versions of python (2 and\n3).  This ensures that no change I make to the code breaks either installation\nor any of the features that I have written tests for.\n\nEvery change to this code is also recompiled automatically, bundled into a\n`conda` package, and made available for download from\n[anaconda.org](https://anaconda.org/moble/scri).  Again, because this is an\nopen-source project all those nice features are free.\n\nThe work of creating this code was supported in part by the Sherman Fairchild\nFoundation and by NSF Grants No. PHY-1306125 and AST-1333129.\n',
    'author': 'Michael Boyle',
    'author_email': 'michael.oliver.boyle@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/moble/scri',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
