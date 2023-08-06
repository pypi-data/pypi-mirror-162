import setuptools

setuptools.setup(
    name="http_query",
    version="0.0.3",
    packages=setuptools.find_packages(),
    author="Tilak Thimmappa",
    description="Dont install this package, purely testing purpose",
    entry_points={
        'console_scripts': [
            'http_query = http_query.http_query:main'
        ]
    },
    install_requires= [
        'click',
        'requests'
    ]
)