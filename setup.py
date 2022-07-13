from distutils.core import setup

setup(
    name='SPACE Labelling',
    version='2.0',
    description='Radio measurement labelling utility',
    author='Aaron Empey',
    maintainer='Corentin Louis',
    maintainer_email='corentin.louis@dias.ie',
    packages=['spacelabel'],
    scripts=['spacelabel/spacelabel'],
    install_requires=[
        'wheel',
        'scipy',
        'numpy',
        'matplotlib',
        'shapely',
        'scipy',
        'astropy',
        'h5py',
        'tfcat @ git+https://gitlab.obspm.fr/maser/catalogues/tfcat.git@v0.4.0'
    ]
)
