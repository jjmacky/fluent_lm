from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="FluentLM",
    version="0.1.0",
    author="James Mccammon",
    author_email="james.j.mccammon@gmail.com",
    description="A library for working with and chaining models together",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jjmacky/LMTools",
    packages=find_packages(),
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)