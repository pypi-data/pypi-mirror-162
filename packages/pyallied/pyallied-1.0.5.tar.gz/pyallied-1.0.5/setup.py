import setuptools

with open("README.md", "rb") as fh:
    long_description = fh.read().decode("utf8").replace('\r\n', '\n')

setuptools.setup(
    name="pyallied",                     # This is the name of the package
    version="1.0.5",                        # The initial release version
    author="srinivasaraojyothi@gmail.com",                     # Full name of the author
    description="pyallied - a wrapper based on selenium python",
    url = "https://github.com/srinivasaraojyothi/seleniumpythonactionbot.git",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.9',                # Minimum version requirement of the package
    py_modules=["dragAndDrop","alerts","DropDown","webWaits","windowAndFrame","webElement","pollWait","session","mobAppium"],             # Name of the python package
    package_dir={'pyallied.web':'pyallied/web', 'pyallied.mobile':'pyallied/mobile'},     # Directory of the source code of the package
    install_requires=[]                     # Install other dependencies if any
)