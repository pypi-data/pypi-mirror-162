from setuptools import setup
import os

VERSION = "5.0.0"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="sparv-freeling",
    description="sparv-freeling is now sparv-sbx-freeling",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    version=VERSION,
    install_requires=["sparv-sbx-freeling"],
    classifiers=["Development Status :: 7 - Inactive"],
)
