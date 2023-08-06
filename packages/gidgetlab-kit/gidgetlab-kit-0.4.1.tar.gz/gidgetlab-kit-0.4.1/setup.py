import setuptools

with open("README.md", "r") as f:
    long_description = f.read()


requirements = [
    "gidgetlab",
    "httpx",
    "typer",
    "pydantic",
    "python-dateutil",
]
tests_requires = ["pytest", "pytest-cov", "pytest-asyncio", "pytest-mock"]

setuptools.setup(
    name="gidgetlab-kit",
    author="Benjamin Bertrand",
    author_email="beenje@gmail.com",
    description="Python package to interact with GitLab",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/beenje/gidgetlab-kit",
    license="MIT license",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=requirements,
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="gitlab async",
    extras_require={"tests": tests_requires},
    python_requires=">=3.8",
    entry_points={"console_scripts": ["gidgetlab=gidgetlab_kit.command:app"]},
)
