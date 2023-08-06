from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.2'
DESCRIPTION = 'Symbolic Quantum Information Calculations'


setup(
    name="SymQInfopy",
    version=VERSION,
    author="jmstf94 (Dimitris Stefanopoulos)",
    author_email="<jmstf94@gmail.com>",
    license='MIT',
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['sympy'],
    keywords=['python', 'quantum information', 'entropies', 'quantum','partial trace'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
