from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "raruscloud/README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.5.0'
DESCRIPTION = 'connector to rarus-cloud ESB'
LONG_DESCRIPTION = DESCRIPTION

# Setting up
setup(
    name="raruscloud",
    version=VERSION,
    author="Serloz (Sergey Lozovskoy)",
    author_email="<serloz@rarus.ru>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests', 'loguru'],
    keywords=['python', 'esb', 'rarus'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)