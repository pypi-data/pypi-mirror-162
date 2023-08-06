# rf-otp

    RobotFramework tools provided by QA team

## Documentation
    https://packaging.python.org/en/latest/tutorials/packaging-projects/ 

## Configuration .pypirc 
    File in ~/.pypirc
    https://packaging.python.org/en/latest/specifications/pypirc/
    https://python-packaging.readthedocs.io/en/latest/dependencies.html

## Packaging
### Prerequisite
	Configure python virtual env
	- python -m venv .venv
	Activate pyhton virtual env
	- .venv\Scripts\activate
	Update pip
	- %CD%\.venv\Scripts\python.exe -m pip install --upgrade pip
    Install/Update setuptools
    - pip install --upgrade setuptools
    Intall build package
    - pip install --upgrade build
    Install twine package
    - pip install twine

### Intall package associated to the tools
    Need by biuldOTP.py (repository: https://pypi.org/project/pyotp/)
    - pip install pyotp==2.6.0

### Build the package
    Change version in files:
    - pyproject.toml
    - setup.cfg
    - setup.py
    Build the package
    - python -m build
    Will create files .tar.gz and .whl in ./dist directory

### Upload package
    In current terminal define proxy your proxy
    set PROXY=http://[username]:[password]@proxygeadm.etat-ge.ch:3128
    set HTTP_PROXY=%PROXY%
    set HTTPS_PROXY=%PROXY%

    Execute commande
    - python -m twine upload --repository pypi dist/*
    Or
    - twine upload --repository pypi dist/*

### pip installation
    pip install rf-otp==0.1.11

### pdm installation
    pdm add --save-exact rf-otp==0.1.11

## Project configuration

### Use library in robot file.
    Add the library in robot file
    - Library   rf_otp

    Use the library in robot file
    - ${GENERATE_KEY} Get Otp ${SECRET}

    ${SECRET} is extract from the QR Code as follow:
    QR Code as URI => otpauth://[URL]?secret=[SECRET]&issuer=[TEXTE]
    Extract [SECRET] and use it in statement of your robot file
    - ${SECRET} [SECRET]

    ${GENERATE_KEY} is the variable with the 6 digits code generated.

## Update Version
    Update files:
    - pyproject.toml
    - setup.cfg
    - setup.py

## Documentation
    https://towardsdatascience.com/setuptools-python-571e7d5500f2
### Setuptools Keywords
    For file setup.py
    https://setuptools.pypa.io/en/latest/references/keywords.html
### File: setup.cfg
    Is an ini file containing option defaults for setup.py commands.



