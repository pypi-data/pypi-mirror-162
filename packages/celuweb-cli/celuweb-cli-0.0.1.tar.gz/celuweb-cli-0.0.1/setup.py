from setuptools import setup

setup(
    name='celuweb-cli',
    version='0.0.1',
    install_requires=[
        'click'
    ],
    entry_points={
        'console_scripts': [
            'cwcli=cwcli.cli:cli'
        ]
    },
)