# -*- coding: utf-8 -*-

import setuptools

# https://packaging.python.org/en/latest/
# https://docs.python.org/3/distutils/setupscript.html
setuptools.setup(
    name='owq-tools',
    version='0.0.2',
    author='owq',
    author_email='qaqiowo@gmail.com',
    url='https://owq.world',
    description='owq tool',
    # long_description='',
    # long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),

    # https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
