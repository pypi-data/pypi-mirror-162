from pkg_resources import parse_requirements
from setuptools import setup, find_packages


def load_requirements(fname: str) -> list:
    requirements = []
    with open(fname, 'r', encoding='utf-8') as fp:
        for req in parse_requirements(fp.read()):
            extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
            requirements.append(
                '{}{}{}'.format(req.name, extras, req.specifier)
            )
    return requirements


setup(
    name='elasticsearch-logging',
    version='0.1.0',
    author='XDeepZeroX',
    license='MIT',
    description='Elasticsearch logging',
    long_description=open('README.md').read(),
    url='https://github.com/XDeepZeroX/elasticsearch-logging',
    platforms='all',
    keywords='logging, es, elastic search',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
    ],
    python_requires='>=3.8, <4',
    packages=find_packages(exclude=['tests']),
    install_requires=load_requirements('requirements.txt'),
    extras_require={
        'dev': load_requirements('requirements.dev.txt'),
        'test': load_requirements('requirements.test.txt')
    },
    # entry_points={
    #     'console_scripts': [
    #         '{0}-api = {0}.api.__main__:main'.format(module_name),
    #         '{0}-db = {0}.db.__main__:main'.format(module_name)
    #     ]
    # },
    include_package_data=True
)
