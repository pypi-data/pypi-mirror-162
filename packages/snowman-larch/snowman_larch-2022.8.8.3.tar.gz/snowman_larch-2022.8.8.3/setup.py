# 编写完包源码后，python setup.py sdist生成pip压缩包
# 解压压缩包，python setup.py install  安装自己的包，就可以引用了


from distutils.core import setup
from setuptools import find_packages

setup(name='snowman_larch',  # 包名
      version='2022.8.8.3',  # 版本号
      description='落叶松',
      long_description='落叶松 Larch',
      author='Alvin Zhang',
      author_email='18048587325@163.com',
      url='https://...',
      license='',
      install_requires=[],
      # classifiers=[
      #     'Intended Audience :: Developers',
      #     'Operating System :: OS Independent',
      #     'Natural Language :: Chinese (Simplified)',
      #     'Programming Language :: Python',
      #     'Programming Language :: Python :: 3',
      #     'Programming Language :: Python :: 3.10',
      #     'Topic :: Utilities'
      # ],
      # keywords='',
      packages=['snowman_larch', 'message_sender'],  # 必填
      # include_package_data=True,
      # package_data={'': ['*.yaml', '*.cfg']},
      py_modules=[]
      )
