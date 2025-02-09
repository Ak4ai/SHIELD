from setuptools import setup, find_packages

setup(
    name='movie-script-analyzer',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A project for analyzing movie scripts using graph theory and machine learning.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'numpy',
        'pandas',
        'networkx',
        'scikit-learn',
        'matplotlib'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)