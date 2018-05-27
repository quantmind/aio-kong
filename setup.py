import os

from setuptools import setup, find_packages

import kong


def read(name):
    filename = os.path.join(os.path.dirname(__file__), name)
    with open(filename) as fp:
        return fp.read()


meta = dict(
    version=kong.__version__,
    description=kong.__doc__,
    name='aio-kong',
    author='Luca Sbardella',
    author_email="luca@quantmind.com",
    maintainer_email="luca@quantmind.com",
    url="https://github.com/lendingblock/aio-kong",
    license="BSD",
    long_description=read("readme.md"),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=['aiohttp'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ]
)


if __name__ == '__main__':
    setup(**meta)
