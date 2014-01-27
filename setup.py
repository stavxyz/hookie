from setuptools import setup, find_packages

dependencies = [
    'argcomplete>=0.6.3',
    'argh>=0.23.3',
    'keyring>=3.3',
    'PyYAML>=3.10',
    'requests>=2.1.0',
    ]

setup(
    name='hookie',
    description='Configure webhooks for your github repo',
    keywords='github, webhook, webhooks',
    version='1.0',
    entry_points = {'console_scripts': ['hookie=hookie.hookie:main']},
    packages = find_packages(exclude=['tests']),
    package_data = {'hookie': ['hookie.yaml']},
    author='samstav',
    author_email='smlstvnh@gmail.com',
    install_requires=dependencies,
    license='Apache 2',
    classifiers=["Programming Language :: Python"],
    url='https://github.com/smlstvnh/hookie'
)
