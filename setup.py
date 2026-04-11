from setuptools import setup, find_packages

setup(
    name='AndoLabInstruments',
    version='0.1.1',
    packages=find_packages(), 
    install_requires=[
        'parse',
        'numpy',
        'pandas',
        'pyvisa',
        'pymeasure'
    ],
)
