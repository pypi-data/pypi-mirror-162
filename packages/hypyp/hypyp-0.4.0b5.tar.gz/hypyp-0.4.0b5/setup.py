# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hypyp', 'hypyp.ext.mpl3d']

package_data = \
{'': ['*'], 'hypyp': ['data/*']}

install_requires = \
['astropy>=5.1,<6.0',
 'autoreject>=0.3.1',
 'h5io>=0.1.7,<0.2.0',
 'matplotlib>=3.2.1,<4.0.0',
 'meshio>=5.3.4,<6.0.0',
 'mne-icalabel>=0.2,<0.3',
 'mne>=1.0.3,<2.0.0',
 'numpy>=1.18.3,<2.0.0',
 'pandas>=1.0.3,<2.0.0',
 'scipy>=1.4.1,<2.0.0',
 'statsmodels>=0.13.2,<0.14.0',
 'tqdm>=4.46.0,<5.0.0']

setup_kwargs = {
    'name': 'hypyp',
    'version': '0.4.0b5',
    'description': 'The Hyperscanning Python Pipeline.',
    'long_description': '# HyPyP 🐍〰️🐍\n\nThe **Hy**perscanning **Py**thon **P**ipeline\n\n[![PyPI version shields.io](https://img.shields.io/pypi/v/hypyp.svg)](https://pypi.org/project/HyPyP/) <a href="https://travis-ci.org/ppsp-team/HyPyP"><img src="https://travis-ci.org/ppsp-team/HyPyP.svg?branch=master"></a> [![license](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) [![Mattermost](https://img.shields.io/static/v1?label=chat&message=Mattermost&color=Blue)](https://mattermost.brainhack.org/brainhack/channels/hypyp)\n\n⚠️ This software is in beta and thus should be considered with caution. While we have done our best to test all the functionalities, there is no guarantee that the pipeline is entirely bug-free. \n\n📖 See our [paper](https://academic.oup.com/scan/advance-article/doi/10.1093/scan/nsaa141/5919711) for more explanation and our plan for upcoming functionalities (aka Roadmap).\n\n🤝 If you want to help you can submit bugs and suggestions of enhancements in our Github [Issues section](https://github.com/ppsp-team/HyPyP/issues).\n\n🤓 For the motivated contributors, you can even help directly in the developpment of HyPyP. You will need to install [Poetry](https://python-poetry.org/) (see section below).\n\n## Contributors\nOriginal authors: Florence BRUN, Anaël AYROLLES, Phoebe CHEN, Amir DJALOVSKI, Yann BEAUXIS, Suzanne DIKKER, Guillaume DUMAS\nNew contributors: Ghazaleh RANJBARAN, Quentin MOREAU, Caitriona DOUGLAS, Franck PORTEOUS, Jonas MAGO, Juan C. AVENDANO\n\n## Installation\n\n```\npip install HyPyP\n```\n\n## Documentation\n\nHyPyP documentation of all the API functions is available online at [hypyp.readthedocs.io](https://hypyp.readthedocs.io/)\n\nFor getting started with HyPyP, we have designed a little walkthrough: [getting_started.ipynb](https://github.com/ppsp-team/HyPyP/blob/master/tutorial/getting_started.ipynb)\n\n## Core API\n\n🛠 [io.py](https://github.com/ppsp-team/HyPyP/blob/master/hypyp/io.py) — Loaders (Florence, Anaël, Ghazaleh, Franck, Jonas, Guillaume)\n\n🧰 [utils.py](https://github.com/ppsp-team/HyPyP/blob/master/hypyp/utils.py) — Basic tools (Amir, Florence, Guilaume)\n\n⚙️ [prep.py](https://github.com/ppsp-team/HyPyP/blob/master/hypyp/prep.py) — Preprocessing (ICA & AutoReject) (Anaël, Florence, Guillaume)\n\n🔠 [analyses.py](https://github.com/ppsp-team/HyPyP/blob/master/hypyp/analyses.py) — Power spectral density and wide choice of connectivity measures (Phoebe, Suzanne, Florence, Ghazaleh, Juan, Guillaume)\n\n📈 [stats.py](https://github.com/ppsp-team/HyPyP/blob/master/hypyp/stats.py) — Statistics (permutations & cluster statistics) (Florence, Guillaume)\n\n🧠 [viz.py](https://github.com/ppsp-team/HyPyP/blob/master/hypyp/viz.py) — Inter-brain visualization (Anaël, Amir, Florence, Guillaume)\n\n🎓 [Tutorials](https://github.com/ppsp-team/HyPyP/tree/master/tutorial) - Examples & documentation (Anaël, Florence, Yann, Ghazaleh, Caitriona, Guillaume)\n\n## Poetry installation (only for developpers and adventurous users)\n\nStep 1: ```pip install poetry```\n\nStep 2: ```git clone git@github.com:ppsp-team/HyPyP.git```\n\nStep 3: ```cd HyPyP```\n\nStep 4: ```poetry install```\n\nStep 5: ```poetry shell```\n\nYou can now use ```jupyter notebook``` or ```ipython```!\n\n⚠️ If you need to install a new dependency (not recommended), you have to use `poetry add THE_NAME_OF_THE_LIBRARY` instead of your usual package manager.',
    'author': 'Anaël AYROLLLES',
    'author_email': 'anael.ayrollles@pasteur.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ppsp-team/HyPyP',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
