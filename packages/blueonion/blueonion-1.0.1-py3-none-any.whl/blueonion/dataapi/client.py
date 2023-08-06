# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pro数据接口 
Created on 2017/07/01
@author: polo,Jimmy
@group : tushare.pro
"""

import simplejson as json
from functools import partial
import requests


class DataApi:

    __token = ''
    __http_url = 'http://54.169.163.141:8099/sapi/dataapi/data/collection/companyhub'

    def __init__(self, token, timeout=10):
        """
        Parameters
        ----------
        token: str
            API接口TOKEN，用于用户认证
        """
        self.__token = token
        self.__timeout = timeout

    def query(self, api_name, fields='', **kwargs):
        req_params = {
            'apiToken': self.__token,
            'params': kwargs,
            'fields': fields
        }


        formData = {'apiToken': self.__token, 'pageSize': kwargs['pageSize'], 'pageNo': kwargs['pageNo']}

        res = requests.post(self.__http_url, data=formData, timeout=self.__timeout, headers={'X-Access-Token':''})
        result = json.loads(res.text)
        if result['code'] != 200:
            raise Exception(result['message'])
        data = result['result']
        # columns = fields
        # items = data['items']

        # return pd.DataFrame(items, columns=columns)
        print(data)
        return data

    def __getattr__(self, name):
        return partial(self.query, name)
