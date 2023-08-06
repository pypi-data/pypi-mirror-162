from setuptools import setup, find_packages


setup(
    name='FSAE47_Function_Box_Test',
    version='0.1',
    license='MIT',
    author="Toby Osborne",
    author_email='toby.osborne@fsae.co.nz',
    packages=find_packages('src'),
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    package_dir={'': 'src'},
    url='https://github.com/UOA-FSAE/functionBox',
    keywords='function box',
    install_requires=[
          'scikit-learn',
      ],
)
