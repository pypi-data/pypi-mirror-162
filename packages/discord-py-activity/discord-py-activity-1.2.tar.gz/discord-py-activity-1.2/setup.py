from setuptools import setup, find_packages

long_description = open("README.md").read()[3:]

setup(
    name="discord-py-activity",
    version="1.2",
    license="MIT",
    author="SpaceX1919",
    author_email="edgardbu@gmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    description="A simple library that gives you access to discord activities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lol123123f/Discord-activities",
    keywords="Discord activity",
    install_requires=["discord.py", "requests"],
)
