from distutils.core import setup
from setuptools import find_packages

setup(name='Lugwit_Module',  # 对外我们模块的名字
      version='0.9',  # 版本号
      description='测试本地发布模块',  # 描述
      long_description='测试本地发布模块',  # 描述
      author='Lugwit',  # 作者
      author_email='1485179300@qq.com',
      license='BSD License',
      packages=find_packages(),
      package_dir={'Lugwit_Module': 'Lugwit_Module'},
      include_package_data=True,
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: Software Development :: Libraries'
      ],
      )

# 打包代码  python37 setup.py sdist
# 上传代码  python37 setup.py sdist upload
# 安装模块  pip install Lugwit_Module
'''
pip2.7 install Lugwit_Module==0.9
pip3.7 install Lugwit_Module==0.9
pip3.9 install Lugwit_Module==0.9
"C:\Program Files\Autodesk\Maya2018\bin\mayapy.exe" -m pip install Lugwit_Module==0.9
'''