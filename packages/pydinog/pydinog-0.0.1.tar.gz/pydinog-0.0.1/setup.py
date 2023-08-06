import setuptools

setuptools.setup(
    name="pydinog",
    version="0.0.1",
    author="Ho Anh Tuan",
    author_email="author@example.com",
    description="Sort description",
    long_description="Full description",
    long_description_content_type="text/markdown",
    install_requires=['pygame', 'importlib_resources'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
