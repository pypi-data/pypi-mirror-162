from setuptools import setup, find_packages

long_description = open("README.md").read()

setup(
    name="discord-py-activity",
    version="1.1",
    license="MIT",
    author="SpaceX1919",
    author_email="edgardbu@gmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lol123123f/Discord-activities",
    keywords="Discord activity",
    install_requires=["discord.py", "requests"],
)
