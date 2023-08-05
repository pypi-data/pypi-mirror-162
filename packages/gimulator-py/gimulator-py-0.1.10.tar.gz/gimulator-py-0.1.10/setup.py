import os
import io
from setuptools import setup, find_packages


currentPath = os.path.abspath(os.path.dirname(__file__))

README = None
NAME = 'gimulator-py'
DESCRIPTION = 'Gimulator client for Python'
URL = 'https://github.com/Gimulator/client-python'
EMAIL = 'info@roboepics.com'
AUTHOR = 'RoboEpics Authors'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.10'

REQUIRED = [
    "grpcio",
    "grpcio-tools",
    "protobuf",
]

try:
    with io.open(os.path.join(currentPath, 'README.md'), encoding='utf-8') as f:
        README = '\n' + f.read()
except FileNotFoundError:
    README = DESCRIPTION


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    install_requires=REQUIRED,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    include_package_data=True,
)