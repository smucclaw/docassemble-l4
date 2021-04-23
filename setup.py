import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')
def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

setup(name='docassemble.l4',
      version='0.0.1',
      description=('A docasssemble extension for creating interviews from the L4 programming language.'),
      long_description="# docassemble-l4\r\n\r\nThis is a package that extends docassemble-scasp and docassemble-datatypes\r\nto facilitate the development of interviews from the l4 programming langauge.\r\n\r\n## Installation\r\n\r\nInstall this package using docassemble's package manager from the github source.\r\n\r\n## Use\r\n\r\nDocassemble interviews generated from the l4 programming langauge should include\r\nthe following statement:\r\n\r\n```\r\ninclude:\r\n  - docassemble.l4:l4.yml\r\n```",
      long_description_content_type='text/markdown',
      author='Jason Morris',
      author_email='jmorris@smu.edu.sg',
      license='',
      url='https://docassemble.org',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=['docassemble.datatypes', 'docassemble.scasp', 'networkx'],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/l4/', package='docassemble.l4'),
     )

