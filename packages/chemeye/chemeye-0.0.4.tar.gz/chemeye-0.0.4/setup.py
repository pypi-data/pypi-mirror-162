from setuptools import setup, find_packages


setup(
    name='chemeye',
    version='0.0.4',
    license='MIT',
    author='Jacob Gerlach',
    author_email='jwgerlach00@gmail.com',
    url='https://github.com/jwgerlach00/chemeye',
    description='Visualization toolset for small molecule drug discovery',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'chemeye': ['assets/default_simmat_options.json']},
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'plotly',
        'rdkit',
        'rdkit_pypi',
        'scikit-learn'
    ],
)
