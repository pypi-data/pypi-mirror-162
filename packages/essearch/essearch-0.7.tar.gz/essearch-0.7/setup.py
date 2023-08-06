from setuptools import setup, find_packages


setup(name='essearch',
      version='0.7',
      description='an expand search function of elasticsearch',
      author='SayaGugu',
      author_email='2708475759@qq.com',
      requires=['elasticsearch', 'ijson', 'pprint', 'tqdm'],  # 定义依赖哪些模块
      packages=find_packages(),  # 系统自动从当前目录开始找包
      # 如果有的文件不用打包，则只能指定需要打包的文件
      # packages=['esopt', '__init__'],  # 指定目录中需要打包的py文件，注意不要.py后缀
      license="apache 3.0"
      )
