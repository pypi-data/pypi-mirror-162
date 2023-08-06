from setuptools import setup

setup(
    name='peitho_data',
    version='1.0.3',
    description='An opinionated Python package on Big Data Analytics',
    url='https://github.com/QubitPi/peitho-data',
    author='Jiaqi liu',
    author_email='jiaqixy@prontonmail.com',
    license='Apache-2.0',
    packages=['peitho_data'],
    install_requires=['wordcloud', 'pycodestyle', 'requests', 'sphinx-rtd-theme', 'matplotlib'],
    zip_safe=False,
    include_package_data=True
)
