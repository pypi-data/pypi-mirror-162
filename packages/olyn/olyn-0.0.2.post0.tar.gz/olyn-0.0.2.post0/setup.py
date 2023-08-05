import re
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

os.chdir(here)

with open(
        os.path.join(here, "LONG_DESCRIPTION.rst"), "r", encoding="utf-8"
) as fp:
    long_description = fp.read()

with open('src/olyn/version.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

url = 'https://github.com/Olyn-inc/olyn-sdk-python'

setup(
    name='olyn',
    packages=find_packages(exclude='tests'),
    version=version,
    description='Python client library for the Olyn API',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    keywords='api client olyn token web3 blockchain asset registry',
    author='Olyn, inc',
    author_email='dev@olyn.com',
    url=url,
    download_url='{}/tarball/v{}'.format(url, version),
    license='MIT',
    package_data={'README': ['README.md']},
    install_requires=['requests>=2.7.0', 'urllib3>=1.26.11'],
    python_requires=">=3.4",
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
