#coding=utf-8

'''
Created on 2013-8-21
@author: 微信派 
微信公众平台
'''
from django.db import models

'''
    公众号
'''
class Account(models.Model):
    account = models.CharField(u'微信号',max_length=100,unique=True)#微信号
    appid = models.CharField(u'AppID',max_length=100,blank=True,null=True)#微信账号对应的appid
    appsecret = models.CharField(u'AppSecret',max_length=100,blank=True,null=True)#微信账号对应的secret
    url = models.CharField(u'URL',max_length=255,unique=True)#URL
    token = models.CharField(u'Tocken',max_length=255,unique=True)#生成的token
    granttype = models.CharField(u'GrantType',max_length=100,default='client_credential')
    msgtype = models.IntegerField(u'消息模式',max_length=11,default=1)#消息模式：1-规则回复；2-规则回复+固定回复；3-规则回复+随机回复；4-随机回复；5-固定回复
    msgcount = models.IntegerField(u'消息条数',max_length=11,default=1)#消息类别：1-随机回复单条消息；1-回复msgCount条图文消息
    name = models.CharField(u'名称',max_length=255,blank=True,null=True)#名称
    createTime = models.DateTimeField(u'入库时间',auto_now_add=True)
    
    class Meta:
        db_table = 't_wxcms_account'
        verbose_name = "开发者账号"
        verbose_name_plural = "开发者账号管理"


'''
AccountMsg 是针对开发者模式进行微信平台的开发的消息记录，
这个消息也可以不保存，直接通过服务器端请求客户的网络信息；

账号消息，根据用户发送的消息，微信公众账号固定回复的消息，
微信已经实现，只能针对企业做个性化定制，可以取企业数据，然后展示
消息类型:text,music,news,voice,video,image
'''  
class AccountMsg(models.Model):
    msgType = models.CharField(u'类型',max_length=20,blank=True,null=True)
    inputCode = models.CharField(u'输入',max_length=20,blank=True,null=True)#粉丝输入编码，或者事件消息的key
    enable = models.IntegerField(max_length=11,default=1,null=True)#是否可用
    createTime = models.DateTimeField(u'入库时间',auto_now_add=True)#创建时间
    readCount = models.IntegerField(max_length=11,default=0,null=True)#阅读数
    reviewCount = models.IntegerField(max_length=11,default=0,null=True)#评论数
    favourCount = models.IntegerField(max_length=11,default=0,null=True)#赞数
    wxpAccount = models.ForeignKey(Account,editable=False)
    
    class Meta:
        db_table = 't_wxcms_msg_base'
        verbose_name = "账号文本消息"
        verbose_name_plural = "账号文本消息管理"


'''
账号的文本消息
'''
class AccountText(models.Model):   
    content = models.TextField(u'内容',blank=True,null=True)
    accountMsg = models.OneToOneField(AccountMsg)
    
    class Meta:
        db_table = 't_wxcms_msg_text'
        verbose_name = "账号文本消息"
        verbose_name_plural = "账号文本消息管理"

'''
    账号图文消息
'''
class AccountNews(models.Model):
    title = models.CharField(u'标题',max_length=255,blank=True,null=True)
    author = models.CharField(u'作者',max_length=50,null=True) #作者
    brief = models.CharField(u'简介',max_length=255,blank=True,null=True)
    description = models.TextField(u'描述',blank=True,null=True)
    picUrl = models.CharField(u'图片链接',max_length=255,blank=True,null=True)
    showPic = models.IntegerField(max_length=11,default=0)#是否显示封面
    picPath = models.CharField(u'图片路径',editable=False,max_length=255,blank=True,null=True)
    url = models.CharField(u'链接',max_length=255,blank=True,null=True)
    accountMsg = models.OneToOneField(AccountMsg)
    
    class Meta:
        db_table = 't_wxcms_msg_news'
        verbose_name = "账号图文消息"
        verbose_name_plural = "账号图文消息管理"

'''
账号的图片消息
'''
class AccountImage(models.Model):
    mediaId = models.TextField(u'MediaId',blank=True)
    accountMsg = models.OneToOneField(AccountMsg)
    
    class Meta:
        db_table = 't_wxcms_msg_images'
        verbose_name = "账号图片消息"
        verbose_name_plural = "账号图片消息管理"

'''
账号的语音消息
'''
class AccountVoice(models.Model):
    mediaId = models.TextField(u'MediaId',max_length=100,blank=True)
    accountMsg = models.OneToOneField(AccountMsg)
    
    class Meta:
        db_table = 't_wxcms_msg_voice'
        verbose_name = "账号语音消息"
        verbose_name_plural = "账号语音消息管理"

'''
账号的视频消息
'''
class AccountVideo(models.Model):
    mediaId = models.TextField(u'MediaId',max_length=100,blank=True)
    thumbMediaId = models.TextField(u'ThumbMediaId',max_length=100,blank=True)
    accountMsg = models.OneToOneField(AccountMsg)
    
    class Meta:
        db_table = 't_wxcms_msg_video'
        verbose_name = "账号视频消息"
        verbose_name_plural = "账号视频消息管理"

'''
账号音乐消息
'''
class AccountMusic(models.Model):
    title = models.CharField(u'标题',max_length=255,blank=True,null=True)
    description = models.CharField(u'描述',max_length=255,blank=True,null=True)
    musicUrl = models.CharField(u'音乐链接',max_length=255,blank=True,null=True)
    hqMusicUrl = models.CharField(u'高清音乐链接',max_length=255,blank=True,null=True)
    thumbMediaId = models.CharField(u'ThumbMediaId',max_length=100,blank=True,null=True)
    accountMsg = models.OneToOneField(AccountMsg)
    
    class Meta:
        db_table = 't_wxcms_msg_music'
        verbose_name = "账号音乐消息"
        verbose_name_plural = "账号音乐消息管理"


'''
    微信账号关注者
'''
class AccountFans(models.Model):
    openid = models.CharField(max_length=100,blank=True,null=True,editable=False)
    username = models.CharField(max_length=100,blank=True,null=True)
    nickname = models.CharField(max_length=20,blank=True,null=True)
    wxaccount = models.CharField(max_length=20,blank=True,null=True)
    password = models.CharField(max_length=20,blank=True,null=True)
    gender = models.IntegerField(max_length=11,blank=True,null=True,default=0)
    city = models.CharField(max_length=50,blank=True,null=True)
    province = models.CharField(max_length=50,blank=True,null=True)
    country = models.CharField(max_length=100,blank=True,null=True)
    language = models.CharField(max_length=50,blank=True,null=True)
    headimgurl = models.CharField(max_length=255,blank=True,null=True)
    
    mobile = models.CharField(u'手机号',max_length=20,blank=True,null=True)
    actId = models.IntegerField(max_length=11,blank=True,null=True)
    
    class Meta:
        db_table = 't_wxcms_account_fans'
        verbose_name = "账号Fans"
        verbose_name_plural = "账号Fans管理"  
        

'''
    开发者模式下的账号菜单；
  button的个数2-3个
  sub-button的个数2-5个
'''
class AccountMenu(models.Model):
    type = models.CharField(u'类型',max_length=50,blank=True,null=True)#类型：点击-click，页面-view
    name = models.CharField(u'名称',max_length=100,blank=True,null=True)
    key = models.CharField(u'Key',max_length=255)#菜单的KEY
    url = models.URLField(u'ViewUrl',max_length=255,blank=True,null=True)#view对应的url
    sort = models.IntegerField(u'排序',max_length=11,default=0,null=True)#排序
    parent = models.ForeignKey('self',default=1,null=True)#父菜单id
    wxpAccount = models.ForeignKey(Account,editable=False,null=True)
    
    class Meta:
        db_table = 't_wxcms_account_menu'
        verbose_name = "账号菜单"
        verbose_name_plural = "账号菜单管理"

