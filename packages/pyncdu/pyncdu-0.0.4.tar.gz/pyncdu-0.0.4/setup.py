from setuptools import setup, find_packages


setup(
    name="pyncdu",
    version="0.0.4",
    license="MIT",
    author="Roman Smolnyk",
    author_email="poma23324@gmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://gitlab.com/roman-smolnyk/pyncdu",
    keywords="cross-platform python ncdu",
    install_requires=[
        "prompt_toolkit",
    ],
)
