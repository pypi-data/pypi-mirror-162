import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='mapping_shortcuts',
    version='1.1.0',
    author='Komissarov Andrey',
    author_email='Komissar.off.andrey@gmail.com',
    description='Useful shortcuts for create mappings',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/moff4/shortcuts',
    install_requires=[
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
)
