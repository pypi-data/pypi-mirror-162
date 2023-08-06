import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="color-printtext",
    version="1.0.2",
    author="gx1285",
    description="PrintColor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gx1285/Print-Color",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
)
