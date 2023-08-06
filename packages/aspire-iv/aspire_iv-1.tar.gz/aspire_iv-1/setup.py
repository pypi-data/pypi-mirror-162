from setuptools import setup, find_packages


setup(
    name='aspire_iv',
    version='1',
    license='',
    author="Girish Kumar R M",
    author_email='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='',
    keywords='iv_and_prediction',
    install_requires=[
          'scikit-learn',
      ],

)