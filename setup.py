"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-systemd-support",
    version="1.1.1.1.1",
    description="Library for systemd.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cyberfusion",
    author_email="support@cyberfusion.io",
    url="https://github.com/CyberfusionIO/python3-cyberfusion-systemd-support",
    platforms=["linux"],
    packages=[
        "cyberfusion.SystemdSupport",
    ],
    package_dir={"": "src"},
    data_files=[],
)
