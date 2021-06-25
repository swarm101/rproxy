from setuptools import setup

setup(
    name="rproxy",
    version="0.0.1",
    packages=["rproxy"],
    install_requires=[],
    entry_points={
        "console_scripts": ["rproxy=rproxy.main:main"],
    },
)