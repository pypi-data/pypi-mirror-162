from setuptools import setup, find_packages
from pip._internal.req import parse_requirements

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='catch_ryzen',
    version='0.1',
    license='MIT',
    author='Mark Ruddy',
    author_email='1markruddy@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/mark-ruddy/algo_open_source_verifier',
    install_requires=required,
)
