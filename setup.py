
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))


setup(
    name='Hipposcarus',
    version='0.0.1',
    description="visualization for Mad2 & Kea2",
    url='https://github.com/mfiers42/Hipposcarus',
    author='Mark Fiers',
    author_email='mark.fiers.42@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'bottle',
    ],
    entry_points={
        'console_scripts': [
            'hipposcarus=hipposcarus.cli:deploy',
        ],
    },
)
