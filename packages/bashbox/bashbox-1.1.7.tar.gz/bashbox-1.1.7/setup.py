import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bashbox",
    version="1.1.7",
    author="Bash Elliott",
    author_email="bashelliott@gmail.com",
    description="Textbox package for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rackodo/bashbox",
    project_urls={
        "Bug Tracker": "https://github.com/rackodo/bashbox/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['bashbox'],
    package_dir={"bashbox": "src"},
    package_data={'bashbox': ['themes/*']},
    python_requires=">=3.6",

    include_package_data=True
)
