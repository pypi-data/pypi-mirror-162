import setuptools

pkg_vars = dict()
with open("wordfreak/_version.py") as f:
    exec(f.read(), pkg_vars)

with open("README.md") as f:
    readMe = f.read()

with open("LICENSE") as f:
    license_ = f.read()

setuptools.setup(
    name="wordfreak",
    version=pkg_vars["__version__"],
    author="Joey Greco",
    author_email="joeyagreco@gmail.com",
    description="Word Freak is a Python library that extracts word frequencies from files.",
    long_description_content_type="text/markdown",
    long_description=readMe,
    license=license_,
    packages=setuptools.find_packages(exclude=("test", "docs")),
    install_requires=["PyPDF2",
                      "docx2txt",
                      "setuptools"]
)
