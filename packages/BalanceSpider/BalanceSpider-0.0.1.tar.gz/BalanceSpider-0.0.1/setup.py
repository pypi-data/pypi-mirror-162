import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BalanceSpider",
    version="0.0.1",
    author="vSir",
    author_email="weiguo341@gmail.com",
    description="simple tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nevquit/monitor_msg_tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
    'lxml==4.0.5','requests'
    ]
)