import setuptools

VERSION = '0.98' 
DESCRIPTION = 'DeepMIMO'
LONG_DESCRIPTION = 'DeepMIMOv2 dataset generator library'

# Setting up
setuptools.setup(
        name="DeepMIMO", 
        version=VERSION,
        author="Umut Demirhan, Ahmed Alkhateeb",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license_files = ('LICENSE.txt', ),
        install_requires=['numpy',
                          'scipy',
                          'tqdm'
                          ],
        
        keywords=['python', 'Alpha'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent"
        ],
        package_dir={"": "src"},
        packages=setuptools.find_packages(where="src")
)