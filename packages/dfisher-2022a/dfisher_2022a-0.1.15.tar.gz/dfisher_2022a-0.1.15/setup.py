# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['dfisher_2022a',
 'dfisher_2022a.config',
 'dfisher_2022a.fits',
 'dfisher_2022a.models',
 'dfisher_2022a.models.lmfit',
 'dfisher_2022a.tests']

package_data = \
{'': ['*'], 'dfisher_2022a.tests': ['fixtures/*']}

install_requires = \
['astropy>=5.0.4,<6.0.0',
 'lmfit>=1.0.3,<2.0.0',
 'mpdaf>=3.5,<4.0',
 'numpy>=1.8,<2.0',
 'pandas>=1.4.2,<2.0.0',
 'tables>=3.7.0,<4.0.0',
 'tqdm>=4.64.0,<5.0.0']

extras_require = \
{'docs': ['Sphinx==4.2.0', 'sphinx-rtd-theme==1.0.0']}

setup_kwargs = {
    'name': 'dfisher-2022a',
    'version': '0.1.15',
    'description': 'Spectral analysis code created for the delivery of the DFisher_2022A ADACS MAP project.',
    'long_description': 'dfisher_2022a\n=============\n\nThis project is being developed in the course of delivering the DFisher_2022A ADACS Merit Allocation Program project.\n\n## Installation\n\n#### Pre-requirement:\n* python >=3.8 <3.10\n* HDF5 \n* C compiler\n\n#### Installing with pip\n\n```\npip install dfisher_2022a\n```\n\n## Getting Started\n1. Import the package\n```\n>>> import dfisher_2022a\n```\n2. Read in data cube\n```\n>>> cube = dfisher_2022a.ReadCubeFile("single_gaussian_muse_size.fits").cube\n```\nIf a separate variance file is provide:\n```\n>>> cube = dfisher_2022a.ReadCubeFile("single_gaussian_muse_size.fits", "muse_var.fits").cube\n```\n3. Prepare data for fitting\n```\n>>> p = dfisher_2022a.ProcessedCube(cube, z=0.009, snr_threshold=5.)\n```\n3.1 De-redshift the cube\n```\n>>> p.de_redshift()\n```\n3.2 Select fitting region for a given line\n```\n>>> p.select_region("Halpha", left=20, right=20)\n```\nKeywords `left` and `right` set the wavelength cuts around the given line on both sides, e.g. the selected region is [line-left, line+right]. If this region exceeds the cube wavelength range, a nearest value within the cube will be used instead.\n\n3.3 Filter the cube by SNR threshold\n```\n>>> p.get_snrmap()\n```\n4. Select fitting model\n```\n>>> model = dfisher_2022a.Lm_Const_1GaussModel\n```\nA single Gaussian model is available within this package. Users can customize their own models following developer\'s note.\n\n5. Fit the cube\n```\n>>> cfl = dfisher_2022a.CubeFitterLM(data=p.data, weight=p.weight, x=p.x, model=model, method=\'leastsq\') # accept lmfit.Model.fit kwargs\n>>> cfl.fit_cube()\n```\nAdditional keyword arguments from [lmfit.Model.fit](https://lmfit.github.io/lmfit-py/model.html#model-class-methods) can be passed to the class object as well.\n\n6. Save output\n```\n>>> out = dfisher_2022a.ResultLM()\n>>> out.get_output(p) # get attributes from ProcessedCube object\n>>> out.get_output(cfl)\n>>> out.save()\n```\nAn `out` directory will be generated in the current directory.\n\n7. Read output\nIn the `.out` folder:\n```\nresult.h5\nfitdata/\n```\nwhere `result.h5` stores the fitting result, and `fitdata/` contains processed data used for fitting.\n\n   To read `result.h5` file:\n   ```\n   >>> import pandas as pd\n   >>> store = pd.HDFStore("result.h5")\n   >>> store.keys()\n   [\'/Halpha_Const_1GaussModel\']\n   >>> df = store.get("Halpha_Const_1GaussModel")\n   ```\n8. Check available lines\n```\n>>> dfisher_2022a.EmissionLines\n{\'Halpha\': 6562.819, \'Hb4861\': 4861.333, \'Hdelta\': 4101.742, ...\n```\nThe line information is included in `emission_lines.py`. Users can customize this file (e.g. adding more lines or updating the wavelength) before importing this package. \n\n9. A wraped approach\n\nA wrapper function is available, which encapsulate steps 1-6.\n```\n>>> from dfisher_2022a import fit_lm\n>>> model = dfisher_2022a.Lm_Const_1GaussModel\n>>> fit_lm(cubefile="single_gaussian_muse_size.fits", line="Halpha", model=model, z=0.009, left=20, right=20, snr_threshold=5.)\n```',
    'author': 'J. Hu',
    'author_email': 'jitinghu@swin.edu.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ADACS-Australia/dfisher_2022a',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
