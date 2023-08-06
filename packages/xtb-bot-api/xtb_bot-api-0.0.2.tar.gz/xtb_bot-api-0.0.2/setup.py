from setuptools import setup, find_packages

VERSION = '0.0.2' 
DESCRIPTION = 'Package for XTB api trading bot (in production)'
LONG_DESCRIPTION = '''
This is a bot api for the xtb currently contribute to the project at my github profile

https://github.com/AnthonyAniobi/XTB_API

[Github](https://github.com/AnthonyAniobi/XTB_API)


`profile`


```
Github = profile
```

'''

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