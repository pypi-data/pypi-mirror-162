# -*- coding: utf-8 -*-
from setuptools import setup

with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

setup(
    name='knarto',
    version='0.1.0',
    python_requires='>=3.8',
    py_modules=["knarto"],
    install_requires=install_requires,
    # metadata to display on PyPI
    author="NAV IKT",
    author_email="nada@nav.no",
    description="knada wrapper for quarto",
    license="MIT",
    entry_points={
        'console_scripts': [
            'knarto = knarto:main',
        ],
    },
)
