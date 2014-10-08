from setuptools import setup, find_packages

setup(
    name='cleese',
    packages=find_packages(),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts' : [
            'cleese = cleese.__main__:main',
        ],
    },
    install_requires=[
        'python-mpd2',
    ],
)
