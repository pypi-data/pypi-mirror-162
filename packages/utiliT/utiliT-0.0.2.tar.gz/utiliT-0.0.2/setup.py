from setuptools import setup, find_packages


VERSION = '0.0.2'
DESCRIPTION = 'Python utilities'
LONG_DESCRIPTION = 'A package to help develop code faster through '

# Setting up
setup(
    name="utiliT",
    version=VERSION,
    author="Nakul Upadhya",
    author_email="<nakulupadhya1@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pyyaml', 'pathlib'],
    keywords=['python', 'utilities'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)