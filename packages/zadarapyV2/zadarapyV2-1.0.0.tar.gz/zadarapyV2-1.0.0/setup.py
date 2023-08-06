# coding: utf-8

"""
    zadara api

    zadarapy operations  # noqa: E501

"""


from setuptools import setup, find_packages  # noqa: H301

NAME = "zadarapyV2"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "certifi>=2017.4.17",
    "python-dateutil>=2.1",
    "six>=1.10",
    "urllib3>=1.23"
]
    

setup(
    name=NAME,
    version=VERSION,
    description="zadara api",
    author_email="",
    url="",
    keywords=["zadarapy"],
    install_requires=REQUIRES,
    dependency_links=[
        'http://strato-pypi.dc1:5002/strato/dev'
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    long_description="""\
    VPSA operations  # noqa: E501
    """
)
