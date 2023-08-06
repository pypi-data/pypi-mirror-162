import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requires =["setuptools>=61.0.0", "wheel","pillow","PyPDF2"]

setuptools.setup(
    # pip3 install test-lib
    name="MakePdfEasily", # Replace with your own username
    version="0.0.13",
    author="MakePdfEasily",
    author_email="ali0088552211@gmail.com",
    description="MakePdfEasily",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AliAdnanc7/MakePdfEasily",
    project_urls={
        "Bug Tracker": "https://github.com/AliAdnanc7/MakePdfEasily/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=requires,
)