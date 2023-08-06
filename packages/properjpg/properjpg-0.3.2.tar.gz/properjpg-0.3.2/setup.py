# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['properjpg']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.0.1,<10.0.0']

entry_points = \
{'console_scripts': ['properjpg = properjpg.cli:run']}

setup_kwargs = {
    'name': 'properjpg',
    'version': '0.3.2',
    'description': 'Make any image ready for the web. Fast.',
    'long_description': '.. |pypi| image:: https://img.shields.io/pypi/v/properjpg\n.. |pythonver| image:: https://img.shields.io/pypi/pyversions/properjpg\n.. |downloads| image:: https://img.shields.io/pypi/dm/properjpg\n.. |build| image:: https://img.shields.io/github/workflow/status/vitorrloureiro/properjpg/Tests\n.. |cov| image:: https://img.shields.io/codecov/c/github/vitorrloureiro/properjpg\n.. |wheel| image:: https://img.shields.io/pypi/wheel/properjpg\n.. |license| image:: https://img.shields.io/pypi/l/properjpg\n\n\nProperJPG\n=========\n\n*Make any image ready for the web. Fast.*\n\nProperJPG is a super fast, lightweight CLI app that converts images to jpg. It also resizes them!\n\n|\n\n|pypi| |pythonver| |build| |cov| |wheel| |downloads| |license|\n\n**Actively soliciting contributors!**\n\nFeel free to open a pull request in case you find an issue or a way to improve the \napp. New features are also welcome, considering they don\'t add unecessary complexity to the\nuser experience.\n\nInstallation\n------------\n\n- `Regular`_\n- `Developer`_\n\nRegular\n~~~~~~~\n**Pipx (recommended)**\n   \n::\n\n   pipx install properjpg\n\n**Pip**\n\n::\n\n   pip install properjpg\n\nDeveloper\n~~~~~~~~~\n**Poetry**\n\n::\n\n   poetry add properjpg\n\n**Git**\n\n::\n\n   git clone https://github.com/vitorrloureiro/properjpg\n\nFeatures\n--------\n\n- `Smart resize`_\n- `Multiprocessing`_\n- `Progressive JPG`_\n\nSmart resize\n~~~~~~~~~~~~\n\nIt has a super cool \'smart resize\' functionality.\nIt allows you to set a max width and height, and you can be sure that\nevery image compressed by it will be no larger or taller than what you\nspecify. This \'smart resize\' mode makes sure to don\'t resize images\nthat doesn\'t need to, and also takes in account if it\'s best for an\nimage to be resized based on it\'s width or height.\n\nProgressive JPG\n~~~~~~~~~~~~~~~\n\nImages are saved as progressive JPEG as default. You can disable this behaviour\nwith `-np` flag. Learn more `here <https://www.thewebmaster.com/develop/articles/how-progressive-jpegs-can-speed-up-your-website/>`_\n\nMultiprocessing\n~~~~~~~~~~~~~~~\n\nThis app uses the multiprocessing module to leverage all the power on your computer.\nIt\'ll work faster if you have multiple cores.\n\nHow does it work?\n-----------------\n**This app works in two modes:**\n\n- `"Single file" mode`_\n- `"Directory" mode`_\n\n"Single file" mode\n~~~~~~~~~~~~~~~~~~\nInput an image path and the desired output path.\n\nBasic usage:\n   \n::\n\n   properjpg [input_path] [output_path] -wi=[max_width] -he=[max_height]\n\n\n"Directory" mode\n~~~~~~~~~~~~~~~~\nThis is where this app really shines. Input a directory path and a desired destination\npath and the app will clone the folder struct of the original directory on the output path.\nThen it will look for all images in the input folder and will try to convert (and\nresize, if you setted it to) them.\n\nProperJPG uses multiprocessing to speed up the process.\n\nBasic usage:\n\n::\n\n   properjpg [input_path] [output_path] -d -wi=[max_width] -he=[max_height]\n\n\nCommands\n--------\n\n-h    Shows the help screen.\n-d    Turns on directory mode.\n-o    If set, the encoder will make an extra pass in order to select optimal encoder settings.\n-q    If set, the input will be compressed to the set value (using Pillow library). Choose a value from 1 to 95.\n-np   If set, disables progressive jpeg and saves as baseline instead.\n-wi   Sets the max width.\n-he   Sets the max height.\n-re   Turns on "reduce" mode and set the factore to which the images are to be resized.\n-v    Shows ProperJPG\'s version.\n\n\n\n\nChanges\n-------\n\nv0.3.1\n~~~~~~\n- Added `-v` flag.\n- Changed the behaviour of progressive jpeg. Now, progressive jpeg is the default. Use the `-np` flag to disable it.\n- Default quality is now 85\n\nv0.3.0\n~~~~~~\n\n- Added support for saving progressive jpgs.\n- Decoupled "optimize" and "quality".\n\nv0.2.0\n~~~~~~\n\n- Added "reduce" mode, where you can resize images by a factor.\n\nNotes\n-----\nThis software is in Alpha stage. A lot of things may change, including syntax and dependencies. I\'m looking for help\nto improve this tool in terms of speed, features and code readability. Feel free to make suggestions and improvements!.\nAlso feel free to help me improve the tests 😅\n\nThe goal is to always keep the code with 100% test coverage.\n\nContributing\n------------\n\nRequirements\n~~~~~~~~~~~~\n\nThis repository automatically lints code with flake8 and black, and also runs mypy\nand pytest. Pull requests must pass in all those tests.\n\n- `black <https://github.com/psf/black>`_\n- `flake8 <https://github.com/PyCQA/flake8>`_\n- `mypy <https://github.com/python/mypy>`_\n- `pytest <https://github.com/pytest-dev/pytest>`_\n\nRoadmap\n~~~~~~~\n\n- Improve UI (maybe switch to Click? Add Colorama?).\n   - Add a better progress view when using `"Directory" Mode`_\n- Improve testing.\n- Improve Docs.\n- Improve Performance.\n\nKnown Issues\n~~~~~~~~~~~~\n\nClient\n......\n- None\n\nDev\n...\n- 100% coverage, but tests are a mess.\n- Improve GitHub Action.\n- Create a workflow for :code:`poetry publish --build`\n\nLicense\n-------\n**MIT**\n',
    'author': 'Vitor Loureiro',
    'author_email': 'miseravel.cruller-0o@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vitorrloureiro/properjpg',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
