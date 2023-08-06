import setuptools

setuptools.setup(
    name="prynth",
    version="1.1.0",
    author="Lactua",
    author_email="minedrayxio@gmail.com",
    description="Prynth allows you to print a text with coordinates.",
    long_description="Prynth allows you to print a text with coordinates.",
    long_description_content_type="text/markdown",
    url="https://github.com/lactua/prynth",
    project_urls={
        "Bug Tracker": "https://github.com/lactua/prynth/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)