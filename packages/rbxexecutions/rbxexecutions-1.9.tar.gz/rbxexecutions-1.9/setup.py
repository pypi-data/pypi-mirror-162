from setuptools import setup, find_packages


setup(
    name='rbxexecutions',
    version='1.9',
    license='MIT',
    author="MaGiXx",
    author_email='email@example.com',
    packages=find_packages(),
    url=None,
    description='pip install rbxexecutions',
    keywords='executions',
    install_requires=[
          'aiohttp',
          'disnake',
      ],

)
# luawhitelist.apikey = '8a503d4ef46b4cfd87b2c43f3d688ec4'
# Bot(
#     luawhitelist = luawhitelist, 
#     token = 'MTAwMjYyMzM1MTQwOTM0NDUyMg.GhP9dQ.PlfGTt_HNF4KBQC9cBr8ok5JrMGhAuUujpGV24', 
#     admins = [923657834577678399], 
#     prefix = '.'
# )

# python setup.py sdist

# twine upload dist/*
