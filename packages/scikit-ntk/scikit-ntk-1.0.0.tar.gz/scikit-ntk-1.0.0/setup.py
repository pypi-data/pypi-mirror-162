# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skntk']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0', 'scikit-learn>=1.0.1,<2.0.0']

setup_kwargs = {
    'name': 'scikit-ntk',
    'version': '1.0.0',
    'description': "Implementation of the neural tangent kernel for scikit-learn's Gaussian process module.",
    'long_description': '## Neural Tangent Kernel for `scikit-learn` Gaussian Processes\n\n**scikit-ntk** is implementation of the neural tangent kernel (NTK) for the `scikit-learn` machine learning library as part of "An Empirical Analysis of the Laplace and Neural Tangent Kernels" ([https://arxiv.org/abs/2208.03761](https://arxiv.org/abs/2208.03761)) master\'s thesis.  This library is meant to directly integrate with [`sklearn.gaussian_process`](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.gaussian_process) module.  This implementation of the NTK can be used in combination with other kernels to train and predict with Gaussian process regressors and classifiers. \n\n## Installation\n\n### Dependencies\n\nscikit-ntk requires:\n* Python (>=3.7)\n* scikit-learn (>=1.0.1)\n\n\n### User installation\nIn terminal using `pip` run:\n\n```bash\npip install scikit-ntk\n```\n\n### Usage\nUseage is described in [`examples/usage.py`](https://github.com/392781/scikit-ntk/blob/master/example/usage.py); however, to get started simply import the `NeuralTangentKernel` class:\n\n```py\nfrom skntk import NeuralTangentKernel as NTK\n\nkernel_ntk = NTK(D=3, bias=0.01, bias_bounds=(1e-6, 1e6))\n```\nOnce declared, usage is the same as other `scikit-learn` kernels.\n\n## Citation\n\nIf you use scikit-ntk in your scientific work, please use the following citation:\n```\n@mastersthesis{lencevicius2022laplacentk,\n  author  = "Ronaldas Paulius Lencevicius",\n  title   = "An Empirical Analysis of the Laplace and Neural Tangent Kernels",\n  school  = "California State Polytechnic University, Pomona",\n  year    = "2022",\n  month   = "August",\n  note    = "https://arxiv.org/abs/2208.03761"\n}\n```\nalong with the one listed on the scikit-learn website: [https://scikit-learn.org/stable/about.html#citing-scikit-learn](https://scikit-learn.org/stable/about.html#citing-scikit-learn)\n',
    'author': 'Ronaldas P Lencevičius',
    'author_email': 'rlencevicius@ucsb.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/392781/scikit-ntk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.7,<4.0.0',
}


setup(**setup_kwargs)
