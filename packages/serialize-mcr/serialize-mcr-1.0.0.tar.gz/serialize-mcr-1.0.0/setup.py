import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='serialize-mcr',
    version='1.0.0',
    author='Andrew Ray',
    author_email='mcaray9@gmail.com',
    description='Creating a serializer for data structures',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/millcityrunner/serialize-mcr',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[
        'flask-sqlalchemy',
        'sqlalchemy'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
