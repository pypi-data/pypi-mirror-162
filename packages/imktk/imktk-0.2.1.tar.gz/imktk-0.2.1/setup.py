# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['imktk', 'imktk.dataarray_methods', 'imktk.dataset_methods']

package_data = \
{'': ['*']}

install_requires = \
['netCDF4>=1.5.8,<2.0.0', 'xarray>=0.20.1,<0.21.0']

entry_points = \
{'console_scripts': ['imktk = imktk:main']}

setup_kwargs = {
    'name': 'imktk',
    'version': '0.2.1',
    'description': 'Toolkit provided by IMK at KIT',
    'long_description': '# IMK Toolkit\n\nThis toolkit provides [post-processing scripts](/imktk) developed by members of the\n[Institute of Meteorology and Climate Research (IMK)](https://dev.to/epassaro/keep-your-research-reproducible-with-conda-pack-and-github-actions-339n)\nat the Karlsruhe Institute of Technology (KIT). The goal of this module is to\ngather together python post-processing scripts for the analysis of netCDF data\nand distribute them easily.\n\n> User provided scripts can be imported using the environmental variables `IMKTK_DATAARRAY` and `IMKTK_DATASET`.\n\n## Usage\n\n```python\nimport imktk\n\nds = imktk.tutorial.open_dataset("toy_weather")\nanomaly_free_tmin = ds.tmin.imktk.anomalies()\n```\n\nFor user provided scripts please set up the appropriate environmental variables:\n\n| Supported variables | Description |\n|---|---|\n|`IMKTK_DATAARRAY`| Path to `xr.DataArray` scripts |\n|`IMKTK_DATASET`| Path to `xr.Dataset` scripts |\n|`IMKTK_LOGLEVEL`| Print debugging information: `DEBUG`, `INFO`, `WARNING`, `ERROR` |\n\nEnvironmental variables can be set using `export` command\n\n```bash\nexport IMKTK_DATAARRAY=/path/to/scripts\n```\n\n## Getting Started\n\nThe easiest method to test the module is to use an interactive session with docker.\nIn this environment you will have a Python 3 environment with all necessary dependencies already installed.\n\n```bash\ndocker run -it imktk/imktk:latest bash\n```\n\n> For the brave: You can test the latest release candidate by changing `latest` to `testing`\n\n## Install\n\nChoose one of the following methods to install the package:\n\n1. Install using `pip`\n2. Install using `conda`\n3. Install using `git clone`\n\n> This package supports only Python 3 with version `>=3.7`. If you are using\n> an earlier version of Python please consider updating.\n\n### `pip`\n\nReleases are automatically uploaded to PyPI. Please execute following command\nto install the package.\n\n```bash\npython3 -m pip install imktk\n```\n\n### `conda`\n\nCurrently the package does no support native installation using `conda`\nrespectively `conda-forge`. This feature is on the roadmap and you can follow\nits process using issue [#34](https://github.com/imk-toolkit/imk-toolkit/issues/34).\nThe current workaround for `conda` installation is to use the following steps\nfor any given environment `<env>`.\n\n1. Activate the environment\n\n    ```bash\n    conda activate <env>\n    ```\n\n2. Install using `pip`\n\n    ```bash\n    python3 -m pip install imktk\n    ```\n\n### `git clone`\n\nIt is also possible to install the package natively by cloning the repository.\nIf you are interested in using this method of installation please follow\nthese steps\n\n1. Install build dependencies\n\n    ```bash\n    python3 -m pip install build\n    ```\n\n2. Clone repository\n\n    ```bash\n    git clone https://github.com/imk-toolkit/imk-toolkit.git\n    ```\n\n3. Generate the Python packages\n\n    ```bash\n    python3 -m build  # or `make build`\n    ```\n\n4. Install packages\n\n    ```bash\n    pip3 install dist/imktk-<current.version>-py3-none-any.whl  # or `make install`\n    ```\n\n> Please be aware that this package uses `HDF5` and `netCDF` c-libraries in the\n> backend. If you are installing using `git clone` the `HDF5_DIR` environment\n> variable with the location of the HDF5 header files needs to be set.\n\n## Further reading\n\nIf you are interested in the inner workings of the package and details of the\nimplementation please refer to the embedded [README.md](/imktk/README.md).\n',
    'author': 'Uğur Çayoğlu',
    'author_email': 'Ugur.Cayoglu@kit.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/imk-toolkit/imk-toolkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
