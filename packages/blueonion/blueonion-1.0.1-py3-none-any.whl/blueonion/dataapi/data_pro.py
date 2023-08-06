# -*- coding:utf-8 -*- 
"""
pro init 
Created on 2022/08/10
@author: gmcheng
@group : blueonion.dataapi
@contact: jimmysoa@sina.cn
"""
from blueonion.dataapi import client

PRICE_COLS = ['open', 'close', 'high', 'low', 'pre_close']
FORMAT = lambda x: '%.2f' % x
FREQS = {'D': '1DAY',
         'W': '1WEEK',
         'Y': '1YEAR',
         }


def pro_api(token=''):
    """
    初始化pro API,第一次可以通过ts.set_token('your token')来记录自己的token凭证，临时token可以通过本参数传入
    """
    pro = client.DataApi(token)
    return pro