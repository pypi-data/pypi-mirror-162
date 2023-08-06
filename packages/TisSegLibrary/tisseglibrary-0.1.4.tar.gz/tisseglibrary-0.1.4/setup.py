


"""The setup script."""

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

setup_requirements = ["pytest-runner"]


test_requirements = ["pytest", "pytest-bdd", 'dataclasses; python_version<"2.7"']

setup(
    author="Marina Sandonis",
    author_email="marinasandfer@gmail.com",
    classifiers=[
        "License :: Apache license 2.0 ",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2.6"
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="It gets the 2D/3D segmentation of the abdomen and the thigh",
    license="Apache license 2.0",
    long_description=readme,
    include_package_data=True,
    keywords="tissue segmnetation",
    name="tisseglibrary",
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/MarinaSandonis/TisSegLibrary",
    version="0.1.3",
    zip_safe=False,
)

