from gettext import install
import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="FirstBS_pkg",
    version="0.0.1",
    author="BS",
    author_email="qudtnwkdrns1@naver.com",
    description="Simple Keylogger Program",
    long_description="A keylogger program that controls the client on the server",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[],

)