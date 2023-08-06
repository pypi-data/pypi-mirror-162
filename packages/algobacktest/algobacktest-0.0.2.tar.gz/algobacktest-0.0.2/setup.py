
import setuptools

# Reads the content of your README.md into a variable to be used in the setup below
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='algobacktest',                           # should match the package folder
    packages=['algobacktest'],                     # should match the package folder
    version='0.0.2',                                # important for updates
    license='MIT',                                  # should match your chosen license
    description='Testing installation of Package',
    long_description=long_description,              # loads your README.md
    long_description_content_type="text/markdown",  # README.md is of type 'markdown'
    author='Baris Arat',
    author_email='hello@baristradingtech.com',
    url='https://github.com/algobacktest/',
    install_requires=['pandas==1.4.3',
                      'numpy',
                      'matplotlib==3.5.2',
                      'pandas-datareader==0.10.0'],                  # list all packages that your package uses
    keywords=["pypi", "algobacktest",], #descriptive meta-data
    classifiers=[                                   # https://pypi.org/classifiers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],

)
