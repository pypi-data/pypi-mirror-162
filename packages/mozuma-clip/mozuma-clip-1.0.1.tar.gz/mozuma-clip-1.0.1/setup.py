import os

import pkg_resources
from setuptools import setup, find_packages

setup(
    name="mozuma-clip",
    py_modules=["clip"],
    version="1.0.1",
    description="Contrastive Language-Image Pretraining",
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md")).read(),
    long_description_content_type="text/markdown",
    author="OpenAI",
    url="https://github.com/mozuma/CLIP",
    keywords=["computer vision", "pattern recognition", "machine-learning"],
    license="MIT License",
    data_files=[(".", ["README.md", "requirements.txt"])],
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        str(r)
        for r in pkg_resources.parse_requirements(
            open(os.path.join(os.path.dirname(__file__), "requirements.txt"))
        )
    ],
    include_package_data=True,
    extras_require={'dev': ['pytest']},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: GPU",
        "Environment :: GPU :: NVIDIA CUDA",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Multimedia",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
)