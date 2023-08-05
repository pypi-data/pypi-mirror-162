from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='http_query',
    version='0.0.1',
    packages=['http_query'],
    entry_points={
        'console_scripts': [
            'http_query = http_query:http_query'
        ]
    },
    license='MIT License',
    author='we45',
    author_email='info@we45.com',
    install_requires=[
        'requests',
        'click'
    ],
    description='please dont install it, its a demo library',
    include_package_data=True
)