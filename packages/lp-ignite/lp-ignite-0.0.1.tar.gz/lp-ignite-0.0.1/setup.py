import imp
import os
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

# What packages are required for this module to be executed?
# with open(os.path.join(here, 'requirements.txt')) as f:
#     REQUIRED = f.read().splitlines()
REQUIRED = [
    "pyyaml",
    "scikit-learn==1.0.2",
    "pandas",
    "boto3",
    "moto",
    "pytest",
    "matplotlib",
    "coverage==6.4.1",
    "seaborn==0.11.2",
    "mlflow==1.27.0",
]

# VERSION = imp.load_source('ignite.version', os.path.join('ignite', '__version__.py'))
VERSION = "0.0.1"
README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name="lp-ignite",
    description="Ignite - High-Level utilities library for various tools such as Spark, SnowFlake, MLflow ",
    author="LeasePlan AI Engineering Team",
    python_requires=">=3.7",
    py_modules=['src'],
    long_description=README,
    test_suite='tests',
    package_data={"src": ["py.typed"]},
    version=VERSION,
    install_requires=REQUIRED,
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: System :: Logging',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms='any',
)
