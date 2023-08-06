import os
import subprocess

from setuptools import find_packages, setup

# get setup.py file path.
__here__ = os.path.abspath(os.path.dirname(__file__))


# get the long description from the README file
with open(os.path.join(__here__, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get version from git tag.
_v = subprocess.run(['git', 'describe', '--tags'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()


setup(
    name='inplus',
    version=_v,
    description='efficient input methods.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='kedarr',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
    ],
    keywords='inplus, input, input methods, input methods for python',
    url='https://github.com/kedarrio/inplus',
    license='MIT',
    packages=["inplus"],
    package_dir={"": "src"},
    package=find_packages("src"),
    python_requires='>=3.9'
)
