from setuptools import find_packages, setup

setup(
    name="jlm",
    version="0.2.0-DEV",
    packages=find_packages("src"),
    package_dir={"": "src"},
    author="Takafumi Arakaki",
    author_email="aka.tkf@gmail.com",
    url="https://github.com/tkf/JuliaManager.jl",
    license="MIT",  # SPDX short identifier
    # description="jlm - THIS DOES WHAT",
    long_description=open("README.rst").read(),
    # keywords="KEYWORD, KEYWORD, KEYWORD",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    install_requires=[
        # "SOME_PACKAGE",
    ],
    entry_points={"console_scripts": ["jlm = jlm.cli:main"]},
)
