from setuptools import setup
from os import path

setup(
    name='Aditzak',
    version='0.3.31',    
    description='A Python package to analyse and build Euskera/Basque verbs.',
    long_description=path.join(path.dirname(__file__), "README.md"),
    long_description_content_type="text/markdown",
    url='https://github.com/HCook86/Aditzak/',
    author='',
    author_email='aditzaksoftware@gmail.com',
    license='BSD 2-clause',
    packages=['Aditzak'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 3"
    ],
    include_package_data=True
)