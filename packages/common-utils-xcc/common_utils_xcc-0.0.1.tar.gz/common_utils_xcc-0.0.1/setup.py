from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Common Utility Python package'
LONG_DESCRIPTION = 'All the utility functions used by video migration project'

# Setting up
setup(
    name="common_utils_xcc",
    version=VERSION,
    author="Xiaoyu Charles Chen",
    author_email="x.chen@sky.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python3', 'common_utils'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
