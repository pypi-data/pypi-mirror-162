from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Package for XTB api'
LONG_DESCRIPTION = 'Some long description for the xtb package'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="xtb_bot-api", 
        version=VERSION,
        author="Anthony Aniobi",
        author_email="anthonyaniobi198@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'forex', 'xtb', 'api'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)