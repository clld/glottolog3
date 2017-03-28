from setuptools import setup, find_packages

setup(
    name='glottolog3',
    version='0.0',
    description='glottolog3',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'clldutils>=1.9.5',
        'clld>=3.2.2',
        'clldmpg>=2.0.0',
        'newick>=0.4',
        'markdown',
        'pyglottolog',
    ],
    tests_require=[
        'Webtest',
        'mock',
    ],
    test_suite="glottolog3",
    entry_points={
        'paste.app_factory': ['main=glottolog3:main'],
        'console_scripts': ['glottolog-app=glottolog3.cli:main'],
    })
