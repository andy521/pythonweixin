#coding=utf-8
'''
微信接口类，处理消息等
@author: 微信派
'''
import json
from core.utils import HttpClient
from wxapi.consts import WXAPI
import hashlib

'''
tocken：tocken标签
timestamp：时间戳
nonce：随机数
signature：微信加密签名
'''
def valid_url(tocken,timestamp,nonce,signature): 
    arr = [tocken,timestamp,nonce]
    arr.sort()
    data = ''
    for s in arr :
        data += s
    sha1 = hashlib.sha1() #或hashlib.md5()  
    sha1.update(data)
    _signature = sha1.hexdigest() #生成40位(sha1)或32位(md5)的十六进制字符串  
    if _signature == signature :
        return True
    else:
        return False

'''
获取微信开发者平台凭证
'''
def get_access_token(account):
    url = WXAPI.ACCESS_TOKEN_GET + '?grant_type=%s&appid=%s&secret=%s' %(account.granttype,account.appid,account.appsecret)
    return json.loads(HttpClient.exeGet(url))

'''
创建菜单
'''
def create_menu(account,data):
    token_rst = get_access_token(account)
    if token_rst.get('access_token',None):#获取到了tocken
        url = WXAPI.MENU_CREATE_POST + '?access_token=%s' %token_rst['access_token']
        if isinstance(data,unicode):
            data = data.encode('UTF-8')
        rst_json = HttpClient.exePost(url, data)
        return json.loads(rst_json)
    else:#返回的是错误代码信息
        return token_rst

'''
删除菜单
'''
def delete_menu(account):
    token_rst = get_access_token(account)
    if token_rst.get('access_token',None):#获取到了tocken
        url = WXAPI.MENU_DELETE_GET + '?access_token=%s' %token_rst['access_token']
        return json.loads(HttpClient.exeGet(url))
    else:#返回的是错误代码信息
        return token_rst

'''
查看菜单；
'''
def get_menu(account):
    token_rst = get_access_token(account)
    if token_rst.get('access_token',None):#获取到了tocken
        url = WXAPI.MENU_GET_GET + '?access_token=%s' %token_rst['access_token']
        return json.loads(HttpClient.exePost(url))
    else:
        return token_rst
    
