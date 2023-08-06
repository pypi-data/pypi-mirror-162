import codecs, re
from setuptools import setup
from setuptools import find_packages

# with codecs.open('pypi/README.md', encoding='utf-8') as f: long_description = f.read()
    
with open('pyken/__init__.py', encoding='utf-8') as f:
    version = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read()).group(1)

setup(
    name='pyken',
    version=version,
    url='https://github.com/Guilliu/pyken',
    author='Guillermo Lizcano',
    author_email='guille.lv.97@gmail.com',
    description='Scorecard development with Python',
    packages=find_packages(),
    keywords=['python', 'rating', 'scoring', 'logistic-regression', 'scorecard', 'woe', 'credit-risk', 'autogrouping'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    long_description_content_type='text/markdown',
    long_description='''
# Pyken - Scorecard development with Python

**Pyken** is a Python package with the aim of providing the necessary tools for:

- Grouping variables (both numerical and categorical) in an **automatic and interactive** way.
- Development of **highly customizable scorecards** adaptable to the requirements of each user.

## Source code
Check out the [GitHub](https://github.com/Guilliu/pyken) repository.

## Documentation
You can find useful documentation [here](https://guilliu.github.io/).
''',
)



