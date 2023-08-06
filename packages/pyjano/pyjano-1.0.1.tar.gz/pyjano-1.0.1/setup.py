import os
import inspect
from setuptools import setup
from pyjano.version import version as pyjano_version

# The directory containing this file
this_script_dir = os.path.dirname(inspect.stack()[0][1])

# The text of the README file
with open(os.path.join(this_script_dir, "pip_readme.md"), 'r') as readme_file:
    readme = readme_file.read()

# This call to setup() does all the work
setup(
    name="pyjano",
    version=pyjano_version,
    description="JANA2 python control tool",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/eic/pyjano",
    author="Dmitry Romanov",
    author_email="romanov@jlab.org",
    license="MIT",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["pyjano", "escrun"],
    package_data={'pyjano': ['pyjano/server/templates/*.html',
                             'pyjano/server/static/*.*'
                       ]},
    include_package_data=True,
#    setup_requires=["click", "appdirs"],
#    install_requires=["click", "appdirs"],
#    entry_points={
#        "console_scripts": [
#            "janapy=janapy:ejpm_cli",
#        ]
#    },
)