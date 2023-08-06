# This file is placed in the Public Domain.


from setuptools import setup


def read():
    return open("README.rst", "r").read()


setup(
    name="oplib",
    version="202",
    url="https://github.com/bthate/oplib",
    author="Bart Thate",
    author_email="bthate67@gmail.com",
    description="object programming library",
    long_description=read(),
    license="Public Domain",
    packages=["op"],
    zip_safe=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: Public Domain",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
)
