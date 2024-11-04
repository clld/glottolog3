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
        'clldutils>=3.22.2',
        'clld>=9.2.2',
        'cldfcatalog',
        'clldmpg>=4.2',
        'markdown',
        'newick>=0.4',
        'pyglottolog>=3.0',
        'purl',
        'colander',
    ],
    long_description='',
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        ],
)
