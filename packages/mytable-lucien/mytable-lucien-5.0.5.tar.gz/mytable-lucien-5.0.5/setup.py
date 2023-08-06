import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='mytable-lucien',
    version='5.0.5',
    author='Lucien',
    author_email="myxlc55@outlook.com",
    url="https://github.com/lucienshawls/mytable-lucien",
    description="A simple package for processing data in the form of a table.",
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)