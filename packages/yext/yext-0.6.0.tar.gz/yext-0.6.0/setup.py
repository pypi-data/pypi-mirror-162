import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yext",
    version="0.6.0",
    author="Yext Team",
    author_email="mdavish@yext.com",
    description="Yext API Client for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yext/yext-client-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
