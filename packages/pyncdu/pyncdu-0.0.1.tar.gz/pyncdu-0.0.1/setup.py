from setuptools import setup, find_packages


setup(
    name="pyncdu",
    version="0.0.1",
    license="MIT",
    author="Roman Smolnyk",
    author_email="poma23324@gmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://gitlab.com/roman-smolnyk/pyncdu",
    keywords="NCDU Pyhon",
    install_requires=[
        "prompt_toolkit",
    ],
)
