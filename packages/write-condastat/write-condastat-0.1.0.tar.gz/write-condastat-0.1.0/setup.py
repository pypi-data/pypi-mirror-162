"""
write-condastat
write-condastat makes it easy to collect, filter and save conda statistics to csv files.
"""

from setuptools import setup  # type: ignore

with open("requirements.txt", encoding="utf8") as fp:
    requirements = fp.read().splitlines()

with open("README.md", encoding="utf8") as fp:
    long_description = fp.read()

setup(
    name="write-condastat",
    version="0.1.0",
    description=(
        "write-condastat makes it easy to collect, filter and save conda statistics to csv files."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    packages=["writecondastat"],
    package_dir={"writecondastat": "src/writecondastat"},
    python_requires=">=3.6",
    install_requires=requirements,
    url="https://github.com/veghdev/write-condastat",
    project_urls={
        "Documentation": "https://github.com/veghdev/write-condastat",
        "Source": "https://github.com/veghdev/write-condastat",
        "Tracker": "https://github.com/veghdev/write-condastat/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
)
