#coding=utf-8
from wxcms import models

'''
内存缓存类
'''
class MemoryCached(object):
    
    '''
    获取系统唯一公众号，如果没有，则自动创建一个;
    如果有多个公众号，开发者自行处理
    '''
    @staticmethod
    def get_account():
        account = models.Account()#默认初始化一个，防止数据库中没有数据
        qs = models.Account.objects.filter()#获取唯一的一个公众号,多账号请开发者自行处理
        if qs:
            account = qs[0]
        else:
            tmp = 'pythonweixin'
            account.name = tmp
            account.account = tmp
            account.appid = tmp
            account.appsecret = tmp
            account.url = tmp
            account.token = tmp
            account.msgcount = 5
            account.save()
        return account
    