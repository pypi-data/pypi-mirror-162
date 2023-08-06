# Introduction
This package contains utilities used to extend robot capabilities through python.

# Build DeltekLib
Steps in creating distributable python library
1. Go to DeltekLib folder
2. python setup.py sdist
3. If twine is not yet installed: pip install twine
4. twine upload dist/*

# Usage
Steps in using DeltekLib
1. From the test machine, download the wheel file from the repository
2. Run "pip install DeltekLib --upgrade"
3. Open a robot file and include the needed Library

    *** Settings ***
    
    Library&nbsp;&nbsp;&nbsp;&nbsp;DeltekLib.WinRM

# Contribute
Feel free to add in python libraries that will be useful in test automation.
