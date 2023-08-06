import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="insertmap", # Replace with your own username
    version="0.1.12",
    author="Damien Marsic",
    author_email="damien.marsic@aliyun.com",
    description="Map insertion sites to viral or microbial genome from wgs or lam-pcr data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/damienmarsic/insertmap",
    package_dir={'': 'insertmap'},
    packages=setuptools.find_packages(),
    py_modules=["insertmap"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires='>=3.6',
)
