from setuptools import setup, find_packages


setup(
    name='siumaai',
    version='0.0.2',
    description='a siumaai for nlp',
    license='Apache License 2.0',
    author='Zonzely',
    install_requires=[
        'torch',
        'transformers',
        'pytorch-lightning'
    ],
    packages=find_packages()
)
