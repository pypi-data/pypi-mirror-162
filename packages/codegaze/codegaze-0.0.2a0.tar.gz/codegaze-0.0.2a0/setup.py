import os
from importlib.machinery import SourceFileLoader
from setuptools import setup, find_packages


version = SourceFileLoader('codegaze.version', os.path.join(
    'codegaze', 'version.py')).load_module().VERSION

setup(
    name='codegaze',
    packages=find_packages(exclude=['tests', 'tests.*']),
    # package_data={"neuralqa": ui_files + yaml_file},
    version=version,
    license='MIT',
    description='Codegace: A library for evaluating code generation models',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Victor Dibia',
    url='https://github.com/victordibia/codegaze',
    python_requires='>=3.9',
    # download_url='https://github.com/victordibia/neuralqa/archive/v0.0.2.tar.gz',
    keywords=['NLP', 'Code Generation', 'Machine Learning'],
    install_requires=[
        'openai',
        'Levenshtein'
    ],
    extras_require={
        'test': ['pytest']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        "console_scripts": [
            "codegaze=codegaze.cli:run",
        ]
    }
)
