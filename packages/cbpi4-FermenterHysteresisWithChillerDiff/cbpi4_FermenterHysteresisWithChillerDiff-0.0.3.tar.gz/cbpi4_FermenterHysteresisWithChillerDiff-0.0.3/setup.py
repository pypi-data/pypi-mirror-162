from setuptools import setup

setup(name='cbpi4_FermenterHysteresisWithChillerDiff',
      version='0.0.3',
      description='CraftBeerPi Plugin',
      author='Maxim Strinzha',
      author_email='mstrinzha@gmail.com',
      url='https://github.com/mstrinzha/cbpi4_FermenterHysteresisWithChillerDiff',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4_FermenterHysteresisWithChillerDiff': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4_FermenterHysteresisWithChillerDiff'],
     )