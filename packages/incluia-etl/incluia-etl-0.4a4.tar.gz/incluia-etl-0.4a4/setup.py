import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="incluia-etl",
    version="0.4a4",
    author="Prosperia Social",
    author_email="developers.etl@prosperia.ai",
    description="A library for Incluia related data wrangling.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prosper-ia/incluia-source",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7, <3.10',
    install_requires=[
        "boto3",
        "geopandas",
        "imageio",
        "matplotlib==3.1.2",
        "numpy==1.21.4",
        "opencv-python>=4.0",
        "pandas==1.3.5",
        "Pillow==9.0.1",
        "scikit-learn==1.1.1",
        "shapely",
        "torch",
        "torchvision",
        "tqdm",
    ],
)
