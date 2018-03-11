from setuptools import setup, find_packages

setup(
    name='glottolog3',
    version='0.0',
    author='',
    author_email='',
    description='glottolog3',
    keywords='web pyramid pylons',
    license='Apache 2',
    url='',
    packages=find_packages(),
    platforms='any',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'paste.app_factory': ['main=glottolog3:main'],
        'console_scripts': ['glottolog-app=glottolog3.__main__:main'],
    },
    install_requires=[
        'clld~=4.0',
        'clldmpg~=3.1',
        'clldutils>=1.9.5',
        'markdown',
        'newick>=0.4',
        'pyglottolog~=1.1',
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': ['pytest-clld>=0.4', 'pytest-cov', 'coverage>=4.2'],
    },
    long_description='',
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        ],
)
