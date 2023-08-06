from setuptools import setup, find_packages

packages = find_packages(
    where='.', 
    include=['printj*']
)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name= "printj",
    version="0.1.1",
    author="Jitesh Gosar",
    author_email="gosar95@gmail.com",
    description="Print log info and color text, speak text and helps debugging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jitesh17/printj",
    py_modules=["printj"],
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        
    ],
    python_requires='>=3.6',
)
