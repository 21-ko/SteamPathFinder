from setuptools import find_packages, setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="SteamPathFinder",
    version="0.1.0",
    author="21-ko",
    author_email="dlwlghks8779@naver.com",
    description="A utility module for finding Steam paths",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/21-ko/SteamPathFinder",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
    install_requires=["vdf"],
)
