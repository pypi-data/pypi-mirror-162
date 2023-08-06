import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datedays",
    version="2.1.5",
    author="liang1024",
    author_email="11751155@qq.com",
    description="Welcome to install and use datedays",
    long_description="Get the list of days,   For example:    ['2022-08-05','2022-08-06','2022-08-07', ...]。   pip install datedays",
    long_description_content_type="text/markdown",
    url="https://github.com/liang1024/datedays",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)