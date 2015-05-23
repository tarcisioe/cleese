from setuptools import setup, find_packages

setup(
    name='cleese',
    version='0.5',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts' : [
            'cleese = cleese.__main__:run',
        ],
    },
    install_requires=[
        'python-mpd2==0.5.3',
    ],
)
