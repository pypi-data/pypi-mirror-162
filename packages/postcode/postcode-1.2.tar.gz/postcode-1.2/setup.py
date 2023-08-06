from setuptools import setup, find_packages


setup(
    name='postcode',
    version='1.2',
    license='MIT',
    author="Quentin PETIT",
    author_email='contact@quentinptt.fr',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/quentinptt/postcode',
    keywords='postcode',
    install_requires=[
          'requests',
      ],

)
