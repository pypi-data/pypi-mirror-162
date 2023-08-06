from setuptools import setup
from pathlib import Path

setup(
    name='api-query',
    version='0.1.1',
    description='Tool to generate and run a script to navigate a REST API.',
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url='https://github.com/es1024/api-query',
    license='MIT',
    packages=['api_query'],
    package_data={'api_query': ['py.typed', '__init__.pyi']},
    install_requires=[
        'aiohttp',
        'funcparserlib>=1.0.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Communications',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Utilities',
        'Typing :: Typed',
    ],
    entry_points={
        'console_scripts': [
            'api-query = api_query.main:main',
        ],
    },
)
