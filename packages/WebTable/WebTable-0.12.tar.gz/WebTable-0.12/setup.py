from setuptools import setup, find_packages


setup(name='WebTable',
      version='0.12',
      description='get cleaner tables from url or html',
      author='SayaGugu',
      author_email='2708475759@qq.com',
      requires=['pandas', 'requests', 'opencc', 'openpyxl', 'selenium', 'pyppeteer', 'asyncio'],  # 定义依赖哪些模块
      install_requires=['pandas', 'requests', 'opencc', 'openpyxl', 'selenium', 'pyppeteer', 'asyncio', 'bs4', 'asyncio'],
      packages=find_packages(),  # 系统自动从当前目录开始找包
      # 如果有的文件不用打包，则只能指定需要打包的文件
      # packages=['esopt', '__init__'],  # 指定目录中需要打包的py文件，注意不要.py后缀
      license="GPLv3"
      )
