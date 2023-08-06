from setuptools import setup
#from pathlib import Path

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='fastai-rawpy', # this is the name people would look up to find this package
    version='0.0.3',
    description='fastai-rawpy connects fast.ai with RawPy, so now fast.ai supports RAW image files',
    py_modules=['fastairawpy'], # This should match the name of the module.py file
    install_requires=["fastai","rawpy","opencv-python"],
    #long_description=(Path(__file__).parent/"README.md").read_text(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    #extras_require={"dev":"pytest>=3.7"},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
    ],
    url="https://github.com/lejrn/fastai-RawPy",
    author="Tal Leron",
    author_mail="lrn.tl.dv@gmail.com",
    package_dir={'':'src'}
)