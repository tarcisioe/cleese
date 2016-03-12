from setuptools import setup, find_packages

setup(
    name='cleese',
    packages=find_packages(),
    entry_points={
        'console_scripts' : [
            'cleese = cleese.__main__:run',
        ],
    },
    install_requires=[
        'python-mpd2',
    ],
)
