#coding=utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt

from wxapi import client,process,consts
from pythonweixin.cached import MemoryCached

'''
微信接口请求uri
GET 验证
POST 消息处理
wxact 微信公众号id，这里是获取系统唯一的公众号，如果有多个公众号，开发者根据此参数自行处理
'''
@csrf_exempt
def wx_request(request,wxact):
    if(request.method == 'GET'):#微信平台验证，account.type = 0
        account = MemoryCached.get_account()
        if account:
            timestamp = request.GET['timestamp']
            nonce = request.GET['nonce']
            signature = request.GET['signature']
            echostr = request.GET['echostr']
            token = account.token #token
            if client.valid_url(token, timestamp, nonce, signature):
                #验证通过，将account设置为开发者类型:更新数据库的 enable，type字段
                return HttpResponse(echostr)
        return HttpResponse('error')
    else:#微信平台request的post消息
        xml = request.POST.keys()[0]#post的数据
        account = MemoryCached.get_account()
        if account and xml:
            q_obj = process.get_request_obj(xml.encode('UTF-8'))#获取请求对象dict
            rep_xml = process.generic_response_obj(account,q_obj)#根据account分发处理业务
            if rep_xml:
                return HttpResponse(rep_xml)  
        return HttpResponse('error')

'''
微信接口-创建菜单
'''
def create_wx_menu(request):
    c = {'wx_type':'create'}
    if request.method == 'POST':
        wxAccount = MemoryCached.get_account()
        if wxAccount.appid and wxAccount.appsecret:
            menu_data = process.get_account_wx_menus(wxAccount)
            if menu_data:
                rst_dict = client.create_menu(wxAccount,menu_data)
                if rst_dict and rst_dict.get('errcode',None) == 0:
                    c.update({'success_flag':1,'errormsg':u'创建菜单成功'})#创建菜单成功
                else:
                    errcode = rst_dict.get('errcode',None)
                    c.update({
                              'success_flag':0,
                              'errormsg':'创建菜单失败：' + consts.WXAPI.ERROR_INFO.get(str(errcode),'请检查菜单是否符合规范')
                              })#创建菜单失败
            else:
                c.update({'success_flag':0,'errormsg':u'创建菜单失败：没有菜单可以创建'})#没有菜单可以创建
        else:
            c.update({'success_flag':0,'errormsg':u'请到"账号基本信息"中完善此账号的App Id和App Secret信息'})#没有菜单可以创建
        return render_to_response("common/result.html", c, context_instance=RequestContext(request))
    else:#GET方法请求
        raise Http404()

'''
微信接口-删除菜单
'''
def delete_wx_menu(request):
    c = {'wx_type':'delete'}
    if request.method == 'POST':
        wxAccount = MemoryCached.get_account()
        rst_dict = client.delete_menu(wxAccount)
        if rst_dict and rst_dict.get('menu',None):
            c.update({'success_flag':1,'errormsg':u'删除菜单成功'})#删除菜单成功
        else:
            errcode = rst_dict.get('errcode',None)
            c.update({
                      'success_flag':0,
                      'errormsg':consts.WXAPI.ERROR_INFO[str(errcode)]
                      })#查看菜单失败
        return render_to_response("common/result.html", c, context_instance=RequestContext(request))
    else:
        raise Http404()

    