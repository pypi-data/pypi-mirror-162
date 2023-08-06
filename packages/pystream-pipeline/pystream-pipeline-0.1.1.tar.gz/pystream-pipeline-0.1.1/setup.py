# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pystream',
 'pystream.data',
 'pystream.functional',
 'pystream.pipeline',
 'pystream.stage']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pystream-pipeline',
    'version': '0.1.1',
    'description': 'Python package to create and manage fast parallelized data processing pipeline for real-time application',
    'long_description': '# PyStream - Real Time Python Pipeline Manager\n\nThis package provides tools to build and boost up a python data pipeline for real time processing. This package is managed using [Poetry](https://python-poetry.org/ ).\n\nFor more detailed guidelines, visit this project [documentation](https://pystream-pipeline.readthedocs.io/).\n\n## Concepts\n\nIn general, PyStream is a package, fully implemented in python, that helps you manage a data pipeline and optimize its operation performance. The main feature of PyStream is that it can build your data pipeline in asynchronous and independent multi-threaded stages model, and hopefully multi-process model in the future.\n\nA PyStream **pipeline** is constructed by several **stages**, where each stage represents a single set of data processing operations that you define by your own. When the stages have been defined, the pipeline can be operated in two modes:\n\n- **Serial mode:** In this mode, each stage are executed in blocking fashion. The later stages will only be executed when the previous ones have been executed, and the next data can only be processed if the previous data have been processed by the final stage. There is only one data stream that can be processed at any time.\n- **Parallel mode:** In this mode, each stage live in a separate parallel thread. If a data has been finished being processed by a stage, the results will be send to the next stage. Since each stage runs in parallel, that stage can immediately take next data input if exist and process it immediately. This way, we can process multiple data at one time, thus increasing the throughput of your pipeline.\n\nWhatever the mode you choose, you only need to focus on implementation of your own data processing codes and pack them into several stages. PyStream will handle the pipeline executions including the threads and the linking of stages for you.\n\n## Installation\n\nYou can install this package using `pip`.\n\n```bash\npip install pystream-pipeline\n```\n\nIf you want to build this package from source or develop it, we recommend you to use Poetry. First install Poetry by following the instructions in its documentation site (you can google it). Then clone this repository and install all the dependencies. Poetry can help you do this and it will also setup a new virtual environment for you.\n\n```bash\npoetry install\n```\n\nTo build the wheel file, you can run\n\n```bash\npoetry build\n```\n\nYou can find the wheel file inside `dist` directory.\n\n## Sample Usage\n\nAPI of PyStream can be found in this project [documentation](https://pystream-pipeline.readthedocs.io/).\nSee `dummy_pipeline.py` to see how PyStream can be used to build a dummy pipeline.\n',
    'author': 'Mukhlas Adib',
    'author_email': 'adib.rasyidy@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MukhlasAdib/pystream-pipeline',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
