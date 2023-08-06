import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name = 'google_trans_new_chiou',
    version = '0.1.0',
    author = 'chiou',
    author_email = 'chiou@e-happy.com.tw',
    description = 'text translation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url = 'https://github.com/chiou3qorz/google_trans_new_chiou',
    packages=setuptools.find_packages(),
    keywords = ['google_translator'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
