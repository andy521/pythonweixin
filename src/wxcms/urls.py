#coding=utf-8

from django.conf.urls import patterns, url
from wxcms import views 

'''
微信公众号cms管理
'''
urlpatterns = patterns('wxcms.views',
    
    #微信url、token
    url(r'^urltoken/$',views.wx_urltoken),#微信接口-创建菜单
    
    #微信账号消息管理
    url(r'^msgtext/(?P<opt>\w+)/$',views.msgtext_manage),#账号文本消息管理
    url(r'^msgnews/(?P<opt>\w+)/$',views.msgnews_manage),#账号图文消息管理
    url(r'^menu/(?P<opt>\w+)/$',views.menu_manage),#账号菜单管理
    
    #微信中图文消息阅读
    url(r'^article/read/$',views.article_read),
)


