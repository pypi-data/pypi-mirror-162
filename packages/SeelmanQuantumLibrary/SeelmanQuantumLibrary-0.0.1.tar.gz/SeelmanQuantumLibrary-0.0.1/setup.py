from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'A library of tools for quantum computing and simulation'
LONG_DESCRIPTION = 'This library contains tools to: 1. Generate many Haar random statevectors using QR matrix decomposition. 2. Generate Haar Random Unitary Gates for initial state randomization. 3. Perform quantum error mitigation via randomized trotterization.'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="SeelmanQuantumLibrary", 
        version=VERSION,
        author="Peter Seelman",
        author_email="<peter.seelman@jhuapl.edu>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['numpy', 'qiskit', 'pennylane'], # add any additional packages that 
        # needs to be installed along with your package.
        
        keywords=['python', 'qiskit', 'haar random'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)