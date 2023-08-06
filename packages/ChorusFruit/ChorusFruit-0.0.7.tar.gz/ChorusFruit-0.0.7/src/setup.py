import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

print('\x1b[34mThanks for Installing \x1b[1m\x1b[35mChorusfruit\x1b[0m')

setuptools.setup(
    name="ChorusFruit",
    version="0.0.1",
    author="manif",
    author_email="example@example.com",
    description="This module is a replacement for curses module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://https://github.com/manifarizi/ChorusFruit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
