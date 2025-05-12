from setuptools import setup, find_packages

setup(
    name="navis-bcf-importer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'bcf2nw=bcf_to_navisworks.core:main',
        ],
    },
    author="Oleg Ariarskiy",
    description="Convert BCF files to Navisworks-compatible XML",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ariarchitect/navis-bcf-importer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
