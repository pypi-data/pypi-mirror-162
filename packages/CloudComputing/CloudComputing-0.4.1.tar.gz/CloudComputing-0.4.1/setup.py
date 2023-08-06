from setuptools import setup, find_packages

VERSION = '0.4.1' 
DESCRIPTION = 'CloudComputing package'
LONG_DESCRIPTION = 'The CloudComputing package can be used to ease remote executing over SSH and cloud storage (OneDrive) with Python.'

# Setting up
setup(
       # the name must match the folder name
        name="CloudComputing", 
        version=VERSION,
        author="Mattia Pesenti",
        author_email="<mattia.pesenti@gmail.com>",
        url="https://github.com/mp1994/CloudComputing",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['cloudsync', 'cloudsync-onedrive', 'pytest'], # add any additional packages that 
        # needs to be installed
        
        keywords=['python', 'cloud computing', 'onedrive'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX :: Linux",
        ]
)