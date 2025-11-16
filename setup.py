"""Setup script for GitHub Sportscaster"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="github-sportscaster",
    version="0.1.0",
    author="OWASP-BLT",
    description="AI-powered GitHub activity announcer with live commentary",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OWASP-BLT/Github_Sportscaster",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sportscaster=sportscaster.app:main",
            "sportscaster-server=sportscaster.server:main",
        ],
    },
)
