import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pubkey2address",
    version="0.0.1",
    author="vSir",
    author_email="weiguo341@gmail.com",
    description="simple tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nevquit/iWAN_Request",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['xrpl-py==1.6.0','coincurve==13.0.0','bit==0.7.2','substrate-interface==1.1']
)