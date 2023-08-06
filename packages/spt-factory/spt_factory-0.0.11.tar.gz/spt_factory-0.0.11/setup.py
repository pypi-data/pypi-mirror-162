#!/usr/bin/env python
from setuptools import find_namespace_packages, setup, find_packages

package_name = "spt_factory"
package_version = "0.0.11"
description = """SPT resource manager"""

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=description,
    author='Mark Poroshin',
    author_email='mporoshin@smartpredictiontech.ru',
    packages=find_namespace_packages(include=[
        'spt_factory',
        'spt_factory.*'
    ]),
    # url="https://gitlab.com/dv_group/dv_elt_lib",
    include_package_data=True,
    install_requires=[
        "psycopg2-binary==2.9.3",
        "pymongo==4.1.1",
        "boto3==1.24.45"
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
      ],
)
