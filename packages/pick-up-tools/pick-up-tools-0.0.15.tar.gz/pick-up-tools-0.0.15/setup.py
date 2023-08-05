#!/usr/bin/env python
import os
from pathlib import Path
from setuptools import setup, find_packages

BASE_DIR = Path(__file__).resolve().parent
setup(name='pick-up-tools',
      version='0.0.15',
      description='just for job',
      long_description=open(os.path.join(BASE_DIR, 'README.md'), 'r').read(),
      long_description_content_type="text/markdown",
      author='pick-up',
      author_email='martinlord@foxmail.com',
      url='https://gitee.com/mahaoyang/pick-up',
      packages=find_packages(include=['pick_up_tools*', ]),
      package_data={'': ['*.txt'], },
      include_package_data=True,
      install_requires=[
          'jieba==0.42.1', 'numpy==1.23.0', 'oss2==2.15.0', 'openpyxl==3.0.10',
          'pandas==1.4.3', 'pyarrow==8.0.0', 'pygtrie==2.4.2', 'pyodps==0.11.0',
          'scikit-learn==1.1.1', 'six==1.16.0', 'torch==1.11.0', 'torchmetrics==0.9.1',
          'tqdm==4.64.0', 'w3lib==1.22.0', 'xlrd==2.0.1', 'xlwt==1.3.0',
          'xmnlp==0.5.2', 'snownlp==0.12.3', 'jiagu==0.2.3', 'jionlp==1.4.14',
      ],
      license='LICENSE.txt',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Operating System :: OS Independent',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3 :: Only",
          'Topic :: Software Development :: Libraries'
      ],
      )
