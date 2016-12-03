from setuptools import setup, find_packages

setup(
    name='cleese',
    version='0.9',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cleese = cleese.__main__:run',
        ],
    },
    install_requires=[
        'python-mpd2>=0.5.5',
        'carl>=0.0.2',
        'wrapt>=1.10.8',
    ],
)
