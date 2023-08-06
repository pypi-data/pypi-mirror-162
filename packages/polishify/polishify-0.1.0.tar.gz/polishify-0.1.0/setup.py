import setuptools
import polishify


setuptools.setup(
    name='polishify',
    version=polishify.__version__,
    packages=['polishify', 'polishify.static'],
    license='MIT',
    description = 'Helps you convert Polish text of unknown encoding into UTF-8',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author = 'Marek Narozniak',
    author_email = 'marek.yggdrasil@gmail.com',
    install_requires=['argparse'],
    url = 'https://github.com/marekyggdrasil/polishify',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['dataset.json'],
    },
    entry_points={
        'console_scripts': [
            'polishify=polishify.polishify:main',
            'polishify-extract=polishify.extract:main'
        ],
    },
)
