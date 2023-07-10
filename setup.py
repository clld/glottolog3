from setuptools import setup, find_packages


setup(
    name='glottolog3',
    version='0.0',
    author='',
    author_email='',
    description='glottolog3',
    keywords='web pyramid pylons',
    license='Apache 2',
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'paste.app_factory': ['main=glottolog3:main'],
        'console_scripts': ['glottolog-app=glottolog3.__main__:main'],
    },
    install_requires=[
        'clld>=9.2.2',
        'cldfcatalog',
        'clldutils>=3.3.0',
        'clldmpg>=4.2',
        'markdown',
        'newick>=0.4',
        'pyglottolog>=3.0',
    ],
    extras_require={
        'dev': [
            'flake8',
            'wheel',
            'twine'
        ],
        'test': [
            'cdstarcat',
            'psycopg2-binary',
            'pytest',
            'pytest-clld>=0.4',
            'pytest-cov',
            'pytest-mock',
            'coverage>=4.2'
            'selenium',
            'webtest',
            'zope.component>=3.11.0',
        ],
    },
    long_description='',
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        ],
)
