import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datedays",
    version="1.5.0",
    author="liang1024",
    author_email="11751155@qq.com",
    description="datedays",
    long_description="# Get the list of days in the format '%y-%m-%d'  。# For example: ['2022-08-05','2022-08-06','2022-08-07', * * *] 。 # Welcome to install and use",
    long_description_content_type="text/markdown",
    url="https://github.com/liang1024/datedays",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)