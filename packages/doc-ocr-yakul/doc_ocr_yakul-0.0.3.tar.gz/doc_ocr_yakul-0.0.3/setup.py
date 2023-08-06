"""
setup file for python package
"""
import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="doc_ocr_yakul",
    version="0.0.3",
    author="Crossml",
    author_email="yakul@crossml.com",
    packages=setuptools.find_packages(),
    description="Text extractor from document",
    long_description=description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords=['easyocr-adaptor', 'easyocr-extractor', 'easyocr'],
    python_requires='>=3',
    install_requires=['easyocr', 'boto3','pdf2image' ]
)

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
