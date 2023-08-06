from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="ft_fibonacci",
    version="1.0.0",
    author="Fahad Taimur",
    author_email="fahadtaimur@protonmail.com",
    description="A simple test package to calculate Fibonacci Sequence through a recursive approach",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fahadtaimur",
    keywords="",  # how packages get indexed on pypi
    license="MIT",
    packages=find_packages(),   # looks for init.py
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
)