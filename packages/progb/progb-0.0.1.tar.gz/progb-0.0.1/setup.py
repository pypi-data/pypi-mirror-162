from setuptools import setup
from os import path

handler = open(path.join(path.dirname(__file__), "README.md"), "r")
README = handler.read()

setup(
    name='progb',
    version='0.0.1',    
    description='A simple python progress bar library',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/HCook86/progressive',
    author='Henry Cook',
    author_email='henryscookolaizola@gmail.com',
    license='',
    packages=['progressive'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers', 
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 3"
    ],
    include_package_data=True
)