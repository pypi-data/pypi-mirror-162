from setuptools import find_packages, setup

with open("requirements.txt", encoding="utf-8") as f:
    REQUIREMENTS = [dependency.strip() for dependency in f if dependency.strip()]

with open("version", encoding="utf-8") as f:
    VERSION = f.read().strip()

setup(
    name="pythemantic",
    version=VERSION,
    description="pythemantic",
    long_description="pythemantic library",
    classifiers=[
        "Programming Language :: Python",
    ],
    author="Khayelihle Tshuma",
    author_email="khayelihle.tshuma@gmail.com",
    url="https://github.com/iamkhaya/pythemantic",
    keywords="python semantic versioning lib",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
)
