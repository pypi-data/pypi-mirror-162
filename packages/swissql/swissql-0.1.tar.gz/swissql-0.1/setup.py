from setuptools import setup, find_packages
 
 
requirements = ["lark>=1.1.2", "sqlfluff>=1.2.1", "sqlglot>=4.2.9"]
 
setup(name='swissql',
      version='0.1',
      url='https://github.com/IPROSpark/SparkSQL-Analyzer',
      license='GNU',
      author='husker Nicialy Quakumei',
      author_email='andrey24072002@bk.ru',
      packages= find_packages(),
      description='Library can help u with sql',
      long_description=open('README.md').read(),
      python_requires=">=3.7.*",)