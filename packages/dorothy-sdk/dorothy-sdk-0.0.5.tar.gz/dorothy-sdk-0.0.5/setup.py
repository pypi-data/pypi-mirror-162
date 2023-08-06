from os.path import join, abspath, dirname
from setuptools import find_packages, setup


def get_version() -> str:
    """Get the package version
    Returns:
        [str]: The package version
    """
    global_names = {}
    exec(  # pylint: disable=exec-used
        open(
            join(
                dirname(abspath(__file__)),
                "dorothy_sdk",
                "version.py"
            )
        ).read(),
        global_names
    )
    return global_names["__version__"]


with open("README.rst", "r") as fh:
    long_description = fh.read()

PACKAGE_NAME = "dorothy-sdk"
PACKAGE_DESCRIPTION = ""
PACKAGE_DOWNLOAD_URL = None
PACKAGE_AUTHOR = "Patrick Braz"
PACKAGE_AUTHOR_EMAIL = "patrickfbraz@poli.ufrj.br"
PACKAGE_MAINTAINER = "Patrick Braz"
PACKAGE_EMAIL = "patrickfbraz@poli.ufrj.br"

setup(
    name=PACKAGE_NAME,
    url="https://github.com/tb-brics/dorothy-sdk",
    description=PACKAGE_DESCRIPTION,
    long_description=long_description,
    version=get_version(),
    download_url=PACKAGE_DOWNLOAD_URL,
    author=PACKAGE_AUTHOR,
    author_email=PACKAGE_AUTHOR_EMAIL,
    maintainer=PACKAGE_MAINTAINER,
    maintainer_email=PACKAGE_EMAIL,
    install_requires=["requests>=2.27.1"],
    packages=find_packages(include=["requirements.txt", ], exclude=[".github", "samples"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)
