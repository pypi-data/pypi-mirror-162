import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("superwise/requirements.txt", "r") as f:
    requirements = [x.strip() for x in f.readlines()]

setuptools.setup(
    name="superwise",
    version="7.1.1",
    description="Superwise SDK",
    url="https://docs.superwise.ai/docs/python-sdk",
    author="Superwise.ai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email="tech@superwise.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(
        include=[
            "superwise",
            "superwise.models",
            "superwise.controller",
            "superwise.controller.summary",
            "superwise.resources",
            "superwise.utils",
            "superwise.utils.storage",
            "superwise.utils.storage.internal_storage",
            "LICENCE",
            "README.md",
            "CHANGELOG.md",
        ],
        exclude=[".*"],
    ),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3",
    setup_requires=[requirements],
    install_requires=[requirements],
)
