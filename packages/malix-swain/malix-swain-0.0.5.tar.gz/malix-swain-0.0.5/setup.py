import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="malix-swain",
    version="0.0.5",
    author="champsunil",
    description="An api for generating disposable mails.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sunilswain/malix",
    project_urls={
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=[
        'temp mail',
        'fake mail',
        'disposable email',
        'api.mail.tm'
    ],
    install_requires=[
        'requests'
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
