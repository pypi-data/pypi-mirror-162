from setuptools import setup

setup(
    name="micropython-phew",
    version="0.0.1",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    project_urls={
        "GitHub": "https://github.com/pimoroni/phew"
    },
    author="Jonathan Williamson",
    maintainer="Phil Howard",
    maintainer_email="phil@pimoroni.com",
    license="MIT",
    license_files="LICENSE",
    py_modules=["phew"]
)
