#!/usr/bin/env python
# coding=utf-8

from config import *

import time
import hashlib
import urllib
import urllib2

def get(**with_given_params):
  req = OpenTaobao(with_given_params)
  return req.get()

class OpenTaobao:
  
  def get(self):
    return self.__parse_result(self.__send_request(self.__generate_query_params()))
  
  def __init__(self, params_dict):
    self.taobaoke_sid = TOP_TAOBAOKE_SID
    self.taobaoke_nick = TOP_TAOBAOKE_NICK
    self.__api_url = TOP_API_URL
    self.__api_secret = TOP_ACCOUNT_TOKEN
    self.__config_options = {
      'api_key':TOP_ACCOUNT_SID,
      'format':'json',
      'v':'2.0',
      'sign_method':'md5',
      'timestamp':time.strftime('%Y-%m-%d %X', time.localtime())
    }
    self.__sign_options = self.__config_options.copy()
    self.__sign_options.update(self.__parse_unicode_params(params_dict))
  
  def __parse_unicode_params(self, dict):
    for k,v in dict.items():
      if isinstance(v,unicode): dict[k] = v.encode('utf-8')
    return dict
  
  def __generate_sign(self):
    param_string = self.__api_secret + ''.join(["%s%s" % (k,v) for k,v in sorted(self.__sign_options.items())]) + self.__api_secret
    md5 = hashlib.md5()
    md5.update(param_string)
    return md5.hexdigest().upper()
  
  def __generate_query_params(self):
    param_options = self.__sign_options.copy()
    param_options['sign'] = self.__generate_sign()
    return urllib.urlencode(param_options)
  
  def __send_request(self, encoded_params):
    rsp = urllib2.urlopen(self.__api_url, encoded_params)
    result = rsp.read()
    rsp.close()
    return result
  
  def __parse_result(self, result):
    data = result.decode('utf-8')
    # TODO
    # converting XML to python dicts
    # if self.__config_options['format'] == 'xml':
    data = eval(data)
    if data.has_key('error_response'):
      data = data["error_response"]
      data = "Error %s: %s" % (data["code"], data["msg"])
    return data
