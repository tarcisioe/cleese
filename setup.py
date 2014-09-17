from setuptools import setup, find_packages

setup(
    name='cleese',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts' : [
            'cleese = cleese.__main__:main',
        ],
    },
    install_requires=[
        'python-mpd2==0.5.3',
    ],
)
