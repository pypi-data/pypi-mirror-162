# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xiaomicaiFibo_pip_fibo",  # 这个名字要独一无二的
    version="0.1",
    author="xmc5281",
    author_email="1028251782@qq.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xmc5281/mymodule",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    py_requires=["xiaomicaiFibo"],  # 这是你存放python代码的目录
    python_requires='>=3.6',
)
