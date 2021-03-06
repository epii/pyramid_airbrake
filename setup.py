from setuptools import Command
from setuptools import find_packages
from setuptools import setup

import os.path

HERE = os.path.abspath(os.path.dirname(__file__))

class PyTest(Command):
    user_options = []
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        from subprocess import call
        import sys
        try:
            ret_val = call(['py.test', 'pyramid_airbrake'] + sys.argv[2:],
                           cwd=HERE)
        except OSError as exc:
            from traceback import print_exc
            from errno import ENOENT
            print_exc(exc)
            errno, strerror = exc
            if errno == ENOENT:
                print "Probably could not find py.test in path; have you run " \
                      "'python setup.py <develop|install>' ?"
            else:
                print ("Unexpected error calling py.test: errno {0}: {1}"
                       .format(errno, strerror))
            ret_val = errno or 1
        raise SystemExit(ret_val)

README_PATH = os.path.join(HERE, 'README.rst')
try:
    README = open(README_PATH).read()
except IOError:
    README = ''

setup(
    name='pyramid_airbrake',
    version='0.2',
    description='',
    long_description=README,
    author='epii',
    author_email='',
    url='',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: OSI Approved :: MIT License",
        ],
    install_requires=[
    'pyramid>=1.2',
    'pytest',
    'threadpool',
    'urllib3',
    ],
    packages=find_packages(),
###    include_package_data=True,
    zip_safe=False,
    cmdclass={'test': PyTest}
    )
