from setuptools import setup
import setuptools
with open("README.md", "r",encoding='utf8') as fh:
    long_description = fh.read()

setup(
    name='requests_qwd',
    version='0.0.3',
    packages=setuptools.find_packages(),
    url='https://github.com/pypa/sampleproject',
    license='MIT',
    author='zyb',
    author_email='1052350468@qq.com',
    description='A small package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
