from setuptools import setup
from importlib import import_module

VERSION = import_module("byemail").__version__
URL = import_module("byemail").__url__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="byemail",
    version=VERSION,
    description="byemail",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: POSIX :: Linux",
        "Topic :: Internet",
        "Programming Language :: Python",
    ],
    keywords="mail asyncio smtp webmail",
    url=URL,
    author="Jeremie Pardou",
    author_email="jeremie.pardou@mhcomm.fr",
    license="Apache Software License",
    packages=["byemail", "byemail.storage", "byemail.helpers", "byemail.middlewares"],
    entry_points={"console_scripts": ["byemail = byemail.commands:run.start"]},
    test_suite="pytest",
    include_package_data=True,
    install_requires=[
        "begins",
        "python-magic",
        "aiosmtpd",
        "arrow",
        "ujson",
        "aiodns",
        "sanic",
        "sanic-auth",
        "tortoise-orm",
        "py-vapid",
        "pywebpush",
        "uvloop",
    ],
    extras_require={},
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)

