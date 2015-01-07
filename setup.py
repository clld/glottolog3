from setuptools import setup, find_packages

requires = [
    'clld>=0.23.1',
    'clldmpg',
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'zope.sqlalchemy',
    'gunicorn',
    'psycopg2',
    'waitress',
    'alembic>=0.7.1',
    ]

setup(name='glottolog3',
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
      install_requires=requires,
      tests_require=requires,
      test_suite="glottolog3",
      entry_points="""\
      [paste.app_factory]
      main = glottolog3:main
      """,
      )
