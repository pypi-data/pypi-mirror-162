from setuptools import setup

setup(
    name='sphinxcontrib-opendataservices',
    version='0.3.1',
    author='Open Data Services',
    author_email='code@opendataservices.coop',
    packages=['sphinxcontrib'],
    url='https://github.com/OpenDataServices/sphinxcontrib-opendataservices',
    install_requires=[
        'docutils',
        'jsonpointer',
        'myst-parser',
        'sphinx',
        'sphinxcontrib-opendataservices-jsonschema>=0.5.0',
    ],
    extras_require={
        'test': [
            'coveralls',
            'flake8',
            'isort',
            'lxml',
            'pytest',
            'pytest-cov',
        ],
    },
    namespace_packages=['sphinxcontrib'],
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ],
)
