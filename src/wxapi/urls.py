#coding=utf-8

from django.conf.urls import patterns, url
from wxapi import views 

'''
微信公众给用户提供的公众url，微信访问公众账号的接口地址  /wxapi/weixinid/
'''
urlpatterns = patterns('wxapi.views',
    
    #微信接口url token认证；消息互动接口
    url(r'^inter/(?P<wxact>[\w-]+)/$', views.wx_request),
    
    #微信菜单接口调用
    url(r'^menu/create/$',views.create_wx_menu),#微信接口-创建菜单
    url(r'^menu/delete/$',views.delete_wx_menu),#微信接口-删除菜单
    
)


