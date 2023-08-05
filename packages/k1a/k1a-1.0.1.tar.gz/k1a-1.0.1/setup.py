#!/usr/bin/env python3

from distutils.core import setup, Extension

module1 = Extension('k1a',
                    sources=['src/demo.cpp'], language="c++", extra_compile_args=["-O3"])

with open("src/demo.cpp") as f:
    version = [l for l in f.readlines(
    ) if "*version" in l][0].split("=")[1].strip().strip(" ").strip(";").strip("\"")

setup(name='k1a',
      version=version,
      description='Accelerated functionalities for k1lib',
      author="Quang Ho",
      author_email="157239q@gmail.com",
      ext_modules=[module1])
