# -*- coding:utf-8 -*- 
import codecs
import os

__version__ = codecs.open(os.path.join(os.path.dirname(__file__), 'VERSION.txt')).read()
__author__ = 'gmcheng'

"""
for blueonion pro api
"""
from blueonion.dataapi.data_pro import (pro_api)
