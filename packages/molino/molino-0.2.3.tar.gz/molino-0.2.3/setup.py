import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "molino",
    version = "0.2.3",
    author = "Benjamín Martínez Mateos",
    author_email = "xaamin@outlook.com",
    description = "Presentation and transformation layer for complex data output",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/xaamin/data-forge",
    project_urls = {
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src/"},
    packages = setuptools.find_packages(where="src/"),
    python_requires = ">=3.0"
)