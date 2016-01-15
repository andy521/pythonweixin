#coding=utf-8

'''
处理不同账号对应的业务，在此作分发
'''
from core.utils import TimeUtil, XmlUtil
from wxapi.consts import MsgType
import wxcms.models as wm
from django.db.models import Q
from django.db import connection,transaction


'''
转换请求的xml 到对应的对象
'''
def get_request_obj(xml):
    q_obj = {}
    root = XmlUtil.getRootNode(xml)
    msgType = XmlUtil.getSingleNodeValue(root,'MsgType')
    
    if msgType == MsgType.TEXT:
        q_obj['Content'] = XmlUtil.getSingleNodeValue(root,'Content')
    elif msgType == MsgType.IMAGE:
        q_obj['PicUrl'] = XmlUtil.getSingleNodeValue(root,'PicUrl')
    elif msgType == MsgType.LOCATION:
        q_obj['Location_X'] = XmlUtil.getSingleNodeValue(root,'Location_X')
        q_obj['Location_Y'] = XmlUtil.getSingleNodeValue(root,'Location_Y')
        q_obj['Scale'] = XmlUtil.getSingleNodeValue(root,'Scale')
        q_obj['Label'] = XmlUtil.getSingleNodeValue(root,'Label')
    else:
        q_obj['Event'] = XmlUtil.getSingleNodeValue(root,'Event')
        q_obj['EventKey'] = XmlUtil.getSingleNodeValue(root,'EventKey')
    
    q_obj['ToUserName'] = XmlUtil.getSingleNodeValue(root,'ToUserName')
    q_obj['FromUserName'] = XmlUtil.getSingleNodeValue(root,'FromUserName')
    q_obj['CreateTime'] = XmlUtil.getSingleNodeValue(root,'CreateTime')
    q_obj['MsgType'] = XmlUtil.getSingleNodeValue(root,'MsgType')
    q_obj['MsgId'] = XmlUtil.getSingleNodeValue(root,'MsgId')
    
    return q_obj

'''
业务处理
返回response dict
'''
def generic_response_obj(account,q_obj):
    msg_type = q_obj['MsgType']
    if msg_type == MsgType.EVENT:#单独处理事件消息
        msg_obj = get_key_event_msg(account,q_obj)#msg_obj
    else:#请求的POST消息
        msg_obj = get_post_msg(account,q_obj)
    
    if msg_obj:
        if isinstance(msg_obj,wm.AccountText):#文本消息
            return get_response_text(q_obj,msg_obj)
        elif isinstance(msg_obj,wm.AccountMusic):#音乐消息
            return get_response_music(q_obj,msg_obj)
        elif isinstance(msg_obj,list):#新闻消息，msg_obj是一个list
            return get_response_news(q_obj,msg_obj)
    return None

'''
获取response_text
''' 
def get_response_text(q_obj,text):
    rep_xml = u'''<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    </xml>''' %(q_obj['FromUserName'],q_obj['ToUserName'],TimeUtil.getIntTime(),text.content)
    return rep_xml.encode('UTF-8')

'''
回复music消息
'''
def get_response_music(q_obj,music):
    rep_xml = u'''<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[music]]></MsgType>
    <Music>
    <Title><![CDATA[%s]]></Title>
    <Description><![CDATA[%s]]></Description>
    <MusicUrl><![CDATA[%s]]></MusicUrl>
    <HQMusicUrl><![CDATA[%s]]></HQMusicUrl>
    </Music>
    </xml>''' %(q_obj['FromUserName'],q_obj['ToUserName'],TimeUtil.getIntTime(),
                music.title,music.description,music.musicUrl,music.hqMusicUrl)
    return rep_xml.encode('UTF-8')

'''
回复新闻消息
'''
def get_response_news(q_obj,news_list):
    rep_xml = u'''<xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>%d</ArticleCount>
    <Articles>''' %(q_obj['FromUserName'],q_obj['ToUserName'],TimeUtil.getIntTime(),len(news_list))

    for new in news_list:
        rep_xml += u'''<item>
        <Title><![CDATA[%s]]></Title>
        <Description><![CDATA[%s]]></Description>
        <PicUrl><![CDATA[%s]]></PicUrl>
        <Url><![CDATA[%s]]></Url>
        </item>''' %(new.title,new.brief,new.picUrl,new.url)#这里使用简介

    rep_xml += '</Articles></xml>' 
    return rep_xml.encode('UTF-8')


#数据库数据处理；
'''
获取具体的account订阅消息;
订阅消息：inputCode = 'subscribe'的消息，如果有多条，默认取第一条
'''
def get_subscribe_event_msg(account):
    try:
        qs = wm.AccountMsg.objects.filter(wxpAccount=account,inputCode='subscribe',enable = 1)
        if qs:
            msg = qs[0]#获取第一条
            return _get_specific_msg(msg)
        return None
    except wm.AccountMsg.DoesNotExist:
        return None

'''
获取具体的account 事件消息：规则回复 和 随机回复
'''
def get_key_event_msg(account,keyname):
    account_msg_type = account.msgType
    account_msg_count = account.msgcount#回复的消息条数；如果是 1 ，只回复一条消息，图文+文本； 如果 >1 回复msgCount条图文消息
    
    if account_msg_count == 1:#是1条消息
        if account_msg_type == 1:#规则回复
            msg = get_rule_msg(account,keyname)
        elif account_msg_type == 2:#规则回复+指定回复
            msg = get_rule_default_msg(account,keyname)
        elif account_msg_type == 3:#规则回复+随机回复
            msg = get_rule_random_msg(account,keyname)
        elif account_msg_type == 5:#固定回复
            msg = get_default_msg(account,keyname)
        else:#随机回复
            msg = get_random_msg(account)
        
        return _get_specific_msg(msg)
    else:#多条消息
        if account_msg_type == 1:#规则回复
            msg = get_rule_msg_more(account,keyname)
        elif account_msg_type == 2:#规则回复+指定回复
            msgs = get_rule_msg_more(account,keyname)
            if msgs:#有规则
                return msgs
            else:#指定回复
                qs = wm.AccountMsg.objects.filter(wxpAccount=account,inputCode=MsgType.DEFAULT,enable = 1)
                if qs:
                    msg = qs[0]#获取第一条
                    return _get_specific_msg(msg)
            return None
        elif account_msg_type == 3:#规则回复+随机回复
            return get_rule_random_msg_more(account,keyname)
        elif account_msg_type == 5:#固定回复
            msg = get_default_msg(account)
            return _get_specific_msg(msg)
        else:#随机回复-4
            return get_random_msg_more(account)
        return None

'''
根据消息ID获取固定消息
'''
def get_fix_event_msg(account,msg_id):
    try:
        if msg_id.find(',') > -1:#多条消息
            qs = wm.AccountMsg.objects.filter(msgType='news',enable=1).filter(pk__in=str.split(','))
            news_list = []
            for n in list(qs):
                news_list.append(n.accountnews)
            return news_list
        else:
            msg = wm.AccountMsg.objects.get(id=int(msg_id),enable = 1)
            return _get_specific_msg(msg)
    except:
        return None

'''
获取具体的POST 数据对应的消息
'''
def get_post_msg(account,input_code):
    #账号消息类型:1-规则回复；2-规则回复+指定回复；3-规则回复+随机回复；4-随机回复；5-固定回复
    account_msg_type = account.msgtype
    account_msg_count = account.msgcount#回复的消息条数；如果是 1 ，只回复一条消息，图文+文本； 如果 >1 回复msgCount条图文消息
    
    if account_msg_count == 1:
        if account_msg_type == 1:#规则回复
            msg = get_rule_msg(account,input_code)
        elif account_msg_type == 2:#规则回复+指定回复
            msg = get_rule_default_msg(account,input_code)
        elif account_msg_type == 3:#规则回复+随机回复
            msg = get_rule_random_msg(account,input_code)
        elif account_msg_type == 5:#固定回复
            msg = get_default_msg(account)
        else:#随机回复-4
            msg = get_random_msg(account)
        return _get_specific_msg(msg)
    
    else:#回复多条图文消息
        if account_msg_type == 1:#规则回复
            msg = get_rule_msg_more(account,input_code)
        elif account_msg_type == 2:#规则回复+指定回复
            msgs = get_rule_msg_more(account,input_code)
            if msgs:#有规则
                return msgs
            else:#指定回复
                qs = wm.AccountMsg.objects.filter(wxpAccount=account,inputCode=MsgType.DEFAULT,enable = 1)
                if qs:
                    msg = qs[0]#获取第一条
                    return _get_specific_msg(msg)
            return None
        elif account_msg_type == 3:#规则回复+随机回复
            return get_rule_random_msg_more(account,input_code)
        elif account_msg_type == 5:#固定回复
            msg = get_default_msg(account)
            return _get_specific_msg(msg)
        else:#随机回复-4
            return get_random_msg_more(account)
        return None

'''
获取规则 + 默认消息
'''
def get_rule_default_msg(account,input_code):
    msg = get_rule_msg(account,input_code)
    if msg:#有规则
        return msg
    else:
        qs = wm.AccountMsg.objects.filter(wxpAccount=account,inputCode=MsgType.DEFAULT,enable = 1)
        if qs:msg = qs[0]#获取第一条
    return msg

'''
固定回复消息
'''
def get_default_msg(account):
    msg = None
    qs = wm.AccountMsg.objects.filter(wxpAccount=account,inputCode=MsgType.DEFAULT,enable = 1)
    if qs:msg = qs[0]#获取第一条
    return msg#获取第一条

'''
获取规则 + 随机消息
'''
def get_rule_random_msg(account,input_code):
    msg = get_rule_msg(account,input_code)
    if msg:#有规则
        return msg
    else:
        return get_random_msg(account) 

'''
获取规则消息
目前是相等的消息
'''
def get_rule_msg(account,input_code):
    if not input_code:
        return None
    qs = wm.AccountMsg.objects.filter(wxpAccount=account,inputCode=input_code,enable=1).extra(select={'rand_value': "rand()"})
    qs = qs.extra(order_by = ['rand_value'])
    if qs:#有规则
        return qs[0]#获取第一条
    return None

'''
获取随机消息
'''
def get_random_msg(account):
    qs = wm.AccountMsg.objects.filter(wxpAccount=account,enable=1).extra(select={'rand_value': "rand()"})
    qs = qs.extra(order_by = ['rand_value'])
    if qs:#有规则
        return qs[0]#获取第一条
    return None

'''
获取规则消息-多条
'''
def get_rule_msg_more(account,input_code):
    if not input_code:
        return None
    
    qs = wm.AccountMsg.objects.filter(wxpAccount=account,msgType='news',enable=1).extra(select={'rand_value': "rand()"})
    q_set = (Q(inputCode__iexact=input_code))#忽略大小写
    qs = qs.filter(q_set)
    qs = qs.extra(order_by = ['rand_value'])[:account.msgcount]
    
    if qs:#有规则
        news_list = []
        for n in list(qs):
            news_list.append(n.accountnews)
        return news_list
    return None

'''
获取随机消息-多条
'''
def get_random_msg_more(account):
    qs = wm.AccountMsg.objects.filter(wxpAccount=account,msgType='news',enable=1).extra(select={'rand_value': "rand()"})
    qs = qs.extra(order_by = ['rand_value'])[:account.msgcount]
    if qs:#有规则
        news_list = []
        for n in list(qs):
            news_list.append(n.accountnews)
        return news_list
    return None


'''
获取规则 + 随机消息 - 多条
'''
def get_rule_random_msg_more(account,input_code):
    msgs = get_rule_msg_more(account,input_code)
    if msgs:#有规则
        return msgs
    else:
        return get_random_msg_more(account) 


'''
搜索消息;没有结果返回订阅消息
'''
def search_post_news_msg(account,input_code):
    qs = wm.AccountMsg.objects.filter(wxpAccount = account,msgType = MsgType.NEWS).order_by('-id')
    q_set = (Q(accountnews__title__icontains=input_code)|Q(accountnews__brief__icontains=input_code))
    qs = qs.filter(q_set)
    if qs:
        if len(qs) > 4:
            qs = qs[0:4]
        news_list = []
        for n in list(qs):
            news_list.append(n.accountnews)
        return news_list
    else:
        msg = get_default_msg(account)
        return _get_specific_msg(msg)


'''
获取具体的消息

对于图文消息
list是针对群发接口准备的，一次性群发多条消息；（目前微信没有提供群发消息接口）
1、目前只支持添加1条消息；
2、如果支持添加大于1条消息了，那么针对用户的请求，会回复多条消息；
'''
def _get_specific_msg(msg):
    if not msg:
        return None
    if msg.msgType == MsgType.TEXT:
        return msg.accounttext
    elif msg.msgType == MsgType.NEWS:
        news = msg.accountnews
        return [news]#此处返回list
    elif msg.msgType == MsgType.MUSIC:
        return msg.accountmusic
    else:
        return None

def get_account_wx_menus(wxpAccount):
    menus = wm.AccountMenu.objects.filter(wxpAccount=wxpAccount).order_by('parent','sort')
    if menus:
        root = {"button":[]}
        buttons = []
        sub_buttons = {}
        for menu in menus:
            if menu.parent.id != 1:
                if menu.parent.id in sub_buttons:
                    if menu.type == 'click':
                        sub_buttons[menu.parent.id].append('{"type":"%s","name":"%s","key":"%s"}' %(menu.type,menu.name,menu.key))
                    else:#'view'
                        sub_buttons[menu.parent.id].append('{"type":"%s","name":"%s","url":"%s"}' %(menu.type,menu.name,menu.url))
                else:
                    if menu.type == 'click':
                        sub_buttons[menu.parent.id] = ['{"type":"%s","name":"%s","key":"%s"}' %(menu.type,menu.name,menu.key)]
                    else:
                        sub_buttons[menu.parent.id] = ['{"type":"%s","name":"%s","url":"%s"}' %(menu.type,menu.name,menu.url)]
            else:
                buttons.append(menu)
        for menu in buttons:
            if menu.id in sub_buttons:
                root["button"].append('{"name":"%s","sub_button":[%s]}' %(menu.name,','.join(sub_buttons[menu.id])))
            else:
                if menu.type == 'click':
                    root["button"].append('{"type":"%s","name":"%s","key":"%s"}' %(menu.type,menu.name,menu.key))
                else:
                    root["button"].append('{"type":"%s","name":"%s","url":"%s"}' %(menu.type,menu.name,menu.url))
        
        buttons = ','.join(root['button'])
        return '{"button":['+ buttons +']"}'.encode("UTF-8")
    else:
        return None
    