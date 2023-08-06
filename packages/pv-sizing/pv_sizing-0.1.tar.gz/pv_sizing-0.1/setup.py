from setuptools import setup, find_packages

setup(
    name='pv_sizing',
    version='0.1',
    license='MIT',
    author="Kiril Ivanov Kurtev",
    author_email='brakisto2015@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/brakisto/PV-sizing',
    keywords='PV sizing',
    install_requires=[
          'numpy',
          'numpy-financial',
          'pandas',
          'pvlib'
      ],

)