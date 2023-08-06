from distutils.core import setup
from setuptools import find_packages

with open("README.rst", "r") as f:
  long_description = f.read()

setup(name='bk-itsm-sdk',  # 包名
      version='1.0.2',  # 版本号
      description='A Itsm-SDK package',
      long_description=long_description,
      author='secloud',
      author_email='869820505@qq.com',
      url='https://bk.tencent.com/docs/',
      install_requires=[
          "certifi==2022.6.15",
          "requests==2.27.1",
          "curlify==2.2.1"
      ],
      license='MIT License',
      packages=find_packages(),
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
          'Topic :: Software Development :: Libraries'
      ],
    )