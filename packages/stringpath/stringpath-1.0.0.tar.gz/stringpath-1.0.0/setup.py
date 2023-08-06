import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stringpath",
    version="1.0.0",
    author="Pascal Vallaster",
    description="StringPath for simulating a 'cd' command in a path-like string",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
    py_modules=["stringpath"],
    package_dir={'':'stringpath/src'},
    install_requires=[]
)