import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automatic-py",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python library for automation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'selenium',
        'webdriver-manager',
        'lxml',
        'pandas',
        'autoit',
        'pytesseract',
        'pillow'
    ],
)
