from setuptools import setup

setup(
   name='pycafe24',
   version='1.4',
   description='A Cafe24 API library',
   author='Sung Jun Hong',
   author_email='sjtheorange@gmail.com',
   packages=['pycafe24'],  #same as name
   install_requires=['requests','six'], #external packages as dependencies
)
