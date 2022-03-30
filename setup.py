from setuptools import find_packages, setup

_dct = {}
with open("tlang/version.py") as f:
    exec(f.read(), _dct)
__version__ = _dct["__version__"]

extras_require = {
    "doc": [
        "sphinx",
        "sphinx-rtd-theme",
        "myst-parser",
        "sphinx-exec-directive",
    ]
}
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tlang",
    description="Transpiler Generator",
    version=__version__,
    license="Apache-2.0",
    author="Alex Eftimiades",
    author_email="alexeftimiades@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["examples"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    package_data={},
    python_requires=">=3.8",
    install_requires=["immutables", "pytest"],
    extras_require=extras_require,
    url="",
    project_urls={
        "Bug Tracker": "",
    },
)
