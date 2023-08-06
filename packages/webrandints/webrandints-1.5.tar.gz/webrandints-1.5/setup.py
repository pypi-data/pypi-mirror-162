from setuptools import setup, find_packages

with open("README.txt", "r") as f1, open("CHANGELOG.txt", "r") as f2:
    long_description = f1.read() + "\n\n" + f2.read()

setup(
   name="webrandints",
   version="1.5",
   author="Vadim Fedulov",
   author_email="vadimfedulov035@gmail.com",
   description="Module to get randints from www.random.org",
   license="GNU GPL v3",
   long_description=long_description,
   keywords=["web", "random", "ints"],
   packages=find_packages(),
   install_requires=["requests"],
)
