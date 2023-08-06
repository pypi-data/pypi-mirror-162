import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datedays",
    version="1.0.0",
    author="liang1024",
    author_email="11751155@qq.com",
    description="date-days",
    long_description="date-days",
    long_description_content_type="text/markdown",
    url="https://github.com/liang1024/datedays",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)