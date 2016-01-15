#coding=utf-8

import uuid
from django.shortcuts import render_to_response,get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect,Http404
from django.core.context_processors import csrf
from django.db import transaction
from PIL import Image

from pythonweixin import settings
from pythonweixin.cached import MemoryCached
from wxcms import models
from wxapi import consts
from core.utils import PaginatorHelper,RegexValidator,get_upload_filename

'''
url token的获取和保存
'''
def wx_urltoken(request):
    c = {'cur_nav':'urltoken'}
    
    #获取唯一的一个公众号,多账号请开发者自行处理
    account = MemoryCached.get_account()
    
    if request.method == 'POST':
        account.account = request.POST['account']
        account.appid = request.POST['appid']
        account.appsecret = request.POST['appsecret']
        
        msgtype = request.POST['msgtype']
        msgcount = request.POST['msgcount']
        account.msgtype = int(msgtype)
        account.msgcount = int(msgcount)
        
        u_ext = account.account
        url = 'http://'+request.get_host()+'/wxapi/inter/%s/' %u_ext
        token = uuid.uuid4().get_hex()
        account.url = url
        account.token = token
        account.save()
        c.update({'successflag':True})
    
    c.update({'account':account})
    c.update(csrf(request))
    return render_to_response("wxcms/urltoken.html", c, context_instance=RequestContext(request))
    
    
#公众号文本消息管理
def msgtext_manage(request,opt):
    c = {'cur_nav':'msgtext'}
    if opt == 'list':
        return msgtext_manage_list(request,c)
    elif opt == 'merge':
        return msgtext_manage_merge(request,c)
    elif opt == 'delete':
        return msgtext_manage_delete(request,c)


#公众号文本消息列表
def msgtext_manage_list(request,c):
    msg_objs = models.AccountMsg.objects.filter(msgType = consts.MsgType.TEXT)
    if request.GET.has_key('page'):
        pageNum = request.GET.get('page')#页码
    else:
        pageNum = 1
    pageSize = 15
    page_dict = PaginatorHelper.paginator_objs(msg_objs, pageNum, pageSize)
    c.update(page_dict)
    return render_to_response('wxcms/msgtext_list.html', c, context_instance=RequestContext(request))


#公众号文本消息merge；此应用中都没有使用form填充model；
def msgtext_manage_merge(request,c):
    if request.method == 'GET':
        if request.GET.has_key('id'):
            id = request.GET['id']
            accountMsg = get_object_or_404(models.AccountMsg,id=id)
            if accountMsg:
                c.update({'accountMsg':accountMsg})
        c.update(csrf(request))
        return render_to_response('wxcms/msgtext_merge.html', c, context_instance=RequestContext(request))
    else:
        accountMsg = models.AccountMsg()
        text = models.AccountText()
        
        if request.POST.get('id',None):#修改
            accountMsg = get_object_or_404(models.AccountMsg,id=request.POST['id'])
            text = accountMsg.accounttext
        else:
            accountMsg.wxpAccount = MemoryCached.get_account()
            
        accountMsg.inputCode = request.POST['inputCode']
        accountMsg.msgType = consts.MsgType.TEXT
        accountMsg.save()
        
        text.content = request.POST['content']
        text.accountMsg = accountMsg
        text.save()
        return HttpResponseRedirect('/wxcms/msgtext/list/')


#公众号文本消息delete
def msgtext_manage_delete(request,c):
    if request.method == 'GET':
        if request.GET.has_key('id'):
            accountMsg = get_object_or_404(models.AccountMsg,id=request.GET['id'])
            accountMsg.delete()
    return HttpResponseRedirect('/wxcms/msgtext/list/')


#公众号图文消息管理
def msgnews_manage(request,opt):
    c = {'cur_nav':'msgnews'}
    if opt == 'list':
        return msgnews_manage_list(request,c)
    elif opt == 'merge':
        return msgnews_manage_merge(request,c)
    elif opt == 'delete':
        return msgnews_manage_delete(request,c)


#公众号图文消息列表
def msgnews_manage_list(request,c):
    msg_objs = models.AccountMsg.objects.filter(msgType = consts.MsgType.NEWS)
    if request.GET.has_key('page'):
        pageNum = request.GET.get('page')#页码
    else:
        pageNum = 1
    pageSize = 15
    page_dict = PaginatorHelper.paginator_objs(msg_objs, pageNum, pageSize)
    c.update(page_dict)
    return render_to_response('wxcms/msgnews_list.html', c, context_instance=RequestContext(request))


#公众号图文消息merge
def msgnews_manage_merge(request,c):
    if request.method == 'GET':
        if request.GET.has_key('id'):
            id = request.GET['id']
            accountMsg = get_object_or_404(models.AccountMsg,id=id)
            if accountMsg:
                c.update({'accountMsg':accountMsg})
        c.update(csrf(request))
        return render_to_response('wxcms/msgnews_merge.html', c, context_instance=RequestContext(request))
    else:
        accountMsg = models.AccountMsg()
        news = models.AccountNews()
        
        if request.POST.get('id',None):#修改
            accountMsg = get_object_or_404(models.AccountMsg,id=request.POST['id'])
            news = accountMsg.accountnews
        else:
            accountMsg.wxpAccount = MemoryCached.get_account()
            
        accountMsg.inputCode = request.POST['inputCode']
        accountMsg.msgType = consts.MsgType.NEWS
        accountMsg.save()
        
        news.title = request.POST.get('title',None)
        news.author = request.POST.get('author',None)
        news.brief = request.POST.get('brief',None)
        news.description = request.POST.get('description',None)
        news.showPic = request.POST.get('showPic',0)
        news.sort = request.POST.get('sort',1)
        
        news.accountMsg = accountMsg
        
        if request.FILES.get('imageFile',None):
            upload = request.FILES['imageFile']
            file_name = upload.name
            if RegexValidator.picture(file_name):
                upload_filename = get_upload_filename('images',file_name)
                image = Image.open(upload)
                image.thumbnail((290,160),Image.ANTIALIAS)#对图片进行等比缩放
                image.save(upload_filename)#保存图片
                news.picPath = upload_filename[len(settings.MEDIA_URL):]
                picUrl = 'http://' + request.get_host() + '/static/%s' %news.picPath
                news.picUrl = picUrl
                
        news.save()
        if request.POST.get('url',None):
            news.url = request.POST['url']
        else:
            news.url = 'http://' + request.get_host() + '/wxcms/article/read/?id=%s' %(str(news.id))
        news.save()
        return HttpResponseRedirect('/wxcms/msgnews/list/')
    

#公众号图文消息delete
def msgnews_manage_delete(request,c):
    if request.method == 'GET':
        if request.GET.has_key('id'):
            accountMsg = get_object_or_404(models.AccountMsg,id=request.GET['id'])
            accountMsg.delete()
    return HttpResponseRedirect('/wxcms/msgnews/list/')


#账号菜单管理
def menu_manage(request,opt):
    c = {'cur_nav':'menu'}
    if opt == 'list':
        return menu_manage_list(request,c)
    elif opt == 'merge':
        return menu_manage_merge(request,c)
    elif opt == 'delete':
        return menu_manage_delete(request,c)


#账号菜单列表
def menu_manage_list(request,c):
    acount = MemoryCached.get_account()#获取系统唯一的公众号
    menu_objs = models.AccountMenu.objects.filter(wxpAccount = acount).order_by('parent','sort')
    c.update({'menu_objs':menu_objs})
    return render_to_response("wxcms/menu_list.html", c, context_instance=RequestContext(request))


#账号菜单创建
def menu_manage_merge(request,c):
    acount = MemoryCached.get_account()#获取系统唯一的公众号
    if request.method == 'GET':
        if request.GET.has_key('id'):
            id = request.GET['id']
            accountMenu = get_object_or_404(models.AccountMenu,id=id)
            if accountMenu:
                c.update({'menu':accountMenu})
        
        rootMenu_qs = models.AccountMenu.objects.filter(id=1)
        if not rootMenu_qs:
            rootMenu = models.AccountMenu()
            rootMenu.id = 1
            rootMenu.parent = models.AccountMenu()
            rootMenu.save()
        else:
            rootMenu = rootMenu_qs[0]
        parent_menus = models.AccountMenu.objects.filter(wxpAccount=acount,parent=rootMenu)
        
        c.update({'parent_menus':parent_menus})
        c.update(csrf(request))
        return render_to_response('wxcms/menu_merge.html', c, context_instance=RequestContext(request))
    else:
        accountMenu = models.AccountMenu()
        if request.POST.get('id',None):#修改
            accountMenu = get_object_or_404(models.AccountMenu,id=request.POST['id'])
        else:#新建
            accountMenu.wxpAccount = MemoryCached.get_account()
        
        accountMenu.name = request.POST['name']
        menuType = request.POST['type']
        accountMenu.url = request.POST['url']
        accountMenu.sort = request.POST['sort']
        
        parentId = request.POST['parentId']
        parentMenu = get_object_or_404(models.AccountMenu,id=parentId)
        accountMenu.parent = parentMenu
            
        accountMenu.type = menuType
        if menuType == 'click':#点击事件
            accountMenu.url = ''
            eventType = request.POST['eventType']
            if eventType == 'key':#关键字消息
                accountMenu.key = request.POST['keyname']
                accountMenu.accountMsgIds = ''
        else:
            accountMenu.url = request.POST['url']
        accountMenu.save()
        return HttpResponseRedirect('/wxcms/menu/list/')


#账号菜单删除
def menu_manage_delete(request,c):
    mid = request.POST['id']
    accountMenu = get_object_or_404(models.AccountMenu,id=mid)
    accountMenu.delete()
    return HttpResponseRedirect('/wxcms/menu/list/')


#图文消息阅读
def article_read(request):
    c = {}
    if request.GET.has_key('id'):
        id = request.GET['id']
        accountMsg = get_object_or_404(models.AccountMsg,id=id)
        if accountMsg:
            c.update({'msg':accountMsg})
    return render_to_response('wxcms/article_read.html', c, context_instance=RequestContext(request))


