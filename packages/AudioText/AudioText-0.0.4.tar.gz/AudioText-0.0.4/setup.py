import setuptools
from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AudioText", # Replace with your own username
    version="0.0.4",
    license='MIT',
    author="Falahgs.G.Saleih",
    author_email="falahgs07@gmail.com",
    description="Convert Arabic Audio To English Text Module ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/falahgs/",
    packages=find_packages(),
    keywords = ['Audio', 'Audio2text'],   # Keywords that define your package best
    install_requires=[ 'gtts','speechrecognition','playsound','pydub','googletrans==3.1.0a0'],
    classifiers=["Programming Language :: Python :: 3","License :: OSI Approved :: MIT License","Operating System :: OS Independent",],
    python_requires='>=3.6',)