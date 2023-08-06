import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='mybase-lucien',
    version='2.1.1',
    author='Lucien',
    author_email="myxlc55@outlook.com",
    url="https://github.com/lucienshawls/mybase-lucien",
    description="This package is used for setting up base locales.",
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)