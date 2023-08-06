"""
Python application component initialization system
"""

from setuptools import setup
from inspect import cleandoc

description = cleandoc(__doc__)

requirements = []

keywords = [
    'asyncio',
    'graceful',
    'init',
    'initializatio',
    'shutdown',
    'manager',
]

classifiers = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Typing :: Typed',
]


py_modules = [
    # 'systemPY',
]

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.md') as history_file:
    history = history_file.read()

long_description = '\n\n'.join((readme, history))


setup(
    classifiers=classifiers,
    description=description,
    install_requires=requirements,
    license="MIT",
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords=keywords,
    name='systemPY',
    py_modules=py_modules,
    url='https://github.com/kai3341/systemPY',
    version='0.0.0',
    zip_safe=True,
)
