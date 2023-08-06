# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File:           setup.py
   Description:
   Author:        
   Create Date:    2020/04/09
-------------------------------------------------
   Modify:
                   2020/04/09:
-------------------------------------------------
"""
from distutils.command.install import INSTALL_SCHEMES
from setuptools import setup, find_packages
from setuptools.command.install import install


for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

setup_args = {
    'cmdclass': {'install': install},
    'name': 'hahaha_utils',
    'author': 'Danny',
    'author_email': 'mrdanny1024@gmail.com',
    'version': "1.1.2",
    'license': 'MIT',
    'description': 'HAHAHA Python3 Utils',
    'long_description': 'HAHAHA Python3 Utils',
    'url': 'https://www.idannywu.com',
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    'classifiers': [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    'package_dir': {
        'hahaha_utils': 'hahaha_utils',
        # 'hahaha_utils.config': 'hahaha_utils/config',
        # 'hahaha_utils.db_utils': 'hahaha_utils/db_utils',
        # 'hahaha_utils.log_handler': 'hahaha_utils/log_handler',
        # 'hahaha_utils.web_request': 'hahaha_utils/web_request'
    },
    'packages': [
        'hahaha_utils',
        # 'hahaha_utils.config',
        # 'hahaha_utils.db_utils',
        # 'hahaha_utils.log_handler',
        # 'hahaha_utils.web_request',
    ],
    # 'packages': find_packages(where="src"),
    'include_package_data': True,
    'install_requires': [
        'pika',
        'pandas',
        'matplotlib',
        'colorama',
        'yagmail',
        'termcolor',
        'camelot_py',
        'requests',
        'kafka_python',
        'pyperclip',
        'lxml',
        'fitz',
        'baidu_aip',
        'scipy',
        'PyMySQL',
        'pyfiglet',
        'opencv_python',
        'numpy',
        'wheel',
        'paramiko',
        'camelot',
        'kafka',
        'Pillow',
        'pip',
        'pycryptodome',
        'elasticsearch',
        'canal-python'
    ],
    'zip_safe': False
}

setup(**setup_args)