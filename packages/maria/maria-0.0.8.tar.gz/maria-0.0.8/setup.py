from os import path
import setuptools

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt')) as f:
    requirements = [l for l in f.read().splitlines()]

setuptools.setup(
    name='maria',
    version='0.0.8',
    description="Simulates atmospheric emission for ground-based telescopes",
    long_description=long_description,
    author="Thomas Morris",
    author_email='thomasmorris@princeton.edu',
    url='https://github.com/tomachito/maria',
    python_requires='>=3.6',
    packages=setuptools.find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    package_data={
        'maria': [
            # When adding files here, remember to update MANIFEST.in as well,
            # or else they will not be included in the distribution on PyPI!
            # 'path/to/data_file',
        ]
    },
    install_requires=requirements,
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
)