from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="pts_lab_smp",
    version="0.0.2",
    author="Pass testing Solutions GmbH",
    description="LAB-SMP PSU Diagnostic Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email="shuparna@pass-testing.de",
    url="https://gitlab.com/pass-testing-solutions/lab-smp-psu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    py_modules=["pts_lab_smp"],
    packages=find_packages(include=['pts_lab_smp']),
    include_package_data=True,
)
