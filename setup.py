from setuptools import setup, find_packages

setup(
    name='maps',
    packages=find_packages(include=('maps', 'maps.*')),
    include_package_data=True,
    install_requires=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'yattag'
    ]
)
