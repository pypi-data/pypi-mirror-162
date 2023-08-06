from setuptools import setup, find_packages


setup(
    name="discord-py-activity",
    version="1.0",
    license="MIT",
    author="SpaceX1919",
    author_email="edgardbu@gmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/lol123123f/Discord-activities",
    keywords="Discord activity",
    install_requires=["discord.py", "requests"],
)
