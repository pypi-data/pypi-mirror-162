import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="comapsmarthome-connected-object-utils",
    version="1.2.0",
    author="Aurélien Sylvan",
    author_email="aurelien.sylvan@comap.eu",
    description="Connected object helpers for ComapSmartHome",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(exclude=["test"]),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
