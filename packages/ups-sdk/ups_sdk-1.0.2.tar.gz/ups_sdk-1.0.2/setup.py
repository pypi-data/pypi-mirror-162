from setuptools import setup, find_packages

# The version of this tool is based on the following steps:
# https://packaging.python.org/guides/single-sourcing-package-version/
VERSION = {}

with open("./UPS_SDK/__init__.py") as fp:
    # pylint: disable=W0122
    exec(fp.read(), VERSION)

setup(
    name="ups_sdk",
    author="Esat Yılmaz",
    author_email="esatyilmaz3500@gmail.com",
    description="UPS Sdk",
    version=VERSION.get("__version__", "1.0.0"),
    packages=find_packages(where=".", exclude=["tests"]),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.9",
    ],
)
