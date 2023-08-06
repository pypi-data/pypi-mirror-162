from distutils.core import setup
from setuptools import find_packages
import os, sys
import sys

try:
    with open('/Users/ymdt/src/DREEM_Herschlag/requirements.txt') as f:
        requirements = f.read().splitlines()
except:
    with open('../requirements.txt') as f:
        requirements = f.read().splitlines()

PYTHON_VERSION = (3,10)

if sys.version_info < PYTHON_VERSION:
    sys.exit(f"Python >= {PYTHON_VERSION[0]}.{PYTHON_VERSION[1]} required.")


setup(
   name='dreem_herschlag',
   version='''1.0.1''',
   license="MIT",
   description='A wrapper for DREEM for the Herschlag lab',
   author='Yves Martin des Taillades',
   author_email='yves@martin.yt',
   long_description= 'TODO',
 #  packages=['DREEM_Herschlag'],  #same as name
   package_dir={'DREEM_Herschlag': 'DREEM_Herschlag'},
   packages=find_packages(),
   package_data={'': ['*.yml']},
   py_modules=[
       'DREEM_Herschlag/sanity_check',
       'DREEM_Herschlag/run_dreem',
       'DREEM_Herschlag/run',
   ],
   include_package_data=True,
   install_requires=requirements, #external packages as dependencies
    entry_points = {
        'console_scripts' : [
            'dreem_herschlag = DREEM_Herschlag.run : main'
        ]
    },
    url='https://github.com/yvesmartindestaillades/DREEM_Herschlag'
)