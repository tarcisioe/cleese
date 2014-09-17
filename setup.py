from setuptools import setup, find_packages

setup(
    name='cleese',
    version='0.3',
    packages=find_packages(),
    entry_points={
        'console_scripts' : [
            'cleese = cleese.__main__:main',
        ],
    },
    install_requires=[
        'python-mpd2',
    ],
)
