from setuptools import setup, find_packages


setup(
    name='jarniadice',
    version='0.1.2',
    license='MIT',
    author='Jader Brasil',
    author_email='jaderbrasil@protonmail.com',
    description="A library for parsing and evaluating Jarnia Dice Notation",
    long_description=open("README.md").read(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/jaderebrasil/python-roller',
    keywords='Dice, Roller, RPG',
    install_requires=[
        'numpy',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Games/Entertainment :: Role-Playing',
        'Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)',
        'Topic :: Games/Entertainment :: Turn Based Strategy',
        'Topic :: Utilities',
    ],
)
