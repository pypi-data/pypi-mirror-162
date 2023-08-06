# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mulfile']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.1,<2.0.0']

setup_kwargs = {
    'name': 'mulfile',
    'version': '0.2.0',
    'description': 'Python library to read .mul and .flm files',
    'long_description': 'mulfile\n=======\n\nMulfile is a Python library for reading .mul and .flm files, acquired by the\nscanning tunneling microscopy (STM) software "SpecsProbe.exe", which is used\nwith the SPM 150 Aarhus by SPECS.\n\n\nInstalling\n----------\n\nInstallation via `pip`_:\n\n.. code-block:: bash\n\n    $ pip install mulfile\n\n.. _pip: https://pip.pypa.io/en/stable/\n\n\nExample Usage\n-------------\n\n.. code-block:: python\n\n    import mulfile as mul\n\n\n    # load a mul or flm file\n    stm_images = mul.load(\'path/to/mulfile.mul\')\n\n\nThis returns all STM-images and their metadata as a list-like object.\nThus, it is possible to access images by indexing and slicing.\n\n.. code-block:: python\n\n    # get the first STM-image\n    image_1 = stm_images[0]\n\n    # get images 1 to 5\n    images = stm_images[0:5]\n\n\nSingle STM-images are stored in objects with their image data (2D numpy array)\nand metadata as `attributes`_.\n\n.. _attributes: https://github.com/matkrin/mulfile/wiki\n\n.. code-block:: python\n\n    # get the image data for image_1\n    image_1.img_data\n\n    # get the bias voltage for image_1\n    image_1.bias\n\n\nIt is also possible to save one or multiple images in the native file format\nof `gwyddion`_ (.gwy)\n\n.. code-block:: python\n\n    # save the complete mul-file as a gwyddion file\n    stm_images.save_gwy(\'output.gwy\')\n\n\n.. _gwyddion: http://gwyddion.net/documentation/user-guide-en/gwyfile-format.html\n\n\nStatus\n------\n\nSTM-images, together with the corresponding metadata, are fully supported  in\nboth .mul and .flm files. Pointscans are not supported yet.\n',
    'author': 'Matthias Krinninger',
    'author_email': 'matkrin@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/matkrin/mulfile',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
