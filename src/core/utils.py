#coding=utf-8
'''
时间工具类
Created on 2013-8-21
@author: weixinpy
'''
import sys,os,random
import time,urllib,urllib2,json,uuid
from xml.dom import minidom
from django.http import HttpResponse
from django.template import Context, loader
from django.core.mail import EmailMultiAlternatives
from django.utils.http import cookie_date

from pythonweixin import settings

'''
时间工具类；
'''
class TimeUtil(object):
    
    '''
    普通类型的数据格式
    '''
    COMMON = '%Y-%m-%d'
    SPLIT = '%Y/%m/%d'
    COMMON_FULL = '%Y-%m-%d %H:%M:%S'
    
    '''
    获取整数时间
    '''
    @staticmethod
    def getIntTime():
        return int(time.time())
    
    '''
    获取时间
    '''
    @staticmethod
    def getTime():
        return time.time()
    
    '''
    获取本地当前时间
    '''
    @staticmethod
    def getLocaltime():
        return time.localtime(time.time())

    '''
    把时间转换为字符串
    '''
    @staticmethod
    def formatCommonText():
        return TimeUtil.formatText(TimeUtil.COMMON)
    
    @staticmethod
    def formatSplitText():
        return TimeUtil.formatText(TimeUtil.SPLIT)
    
    @staticmethod
    def formatCommonFullText():
        return TimeUtil.formatText(TimeUtil.COMMON_FULL)
    
    @staticmethod
    def formatText(pattern,tm=time.time()):
        return time.strftime(pattern,time.localtime(tm))
    
    '''
    把字符串转换为时间
    '''
    @staticmethod
    def parseCommonTime(tx):
        return TimeUtil.parseTime(tx, TimeUtil.COMMON)
    
    @staticmethod
    def parseCommonFullTime(tx):
        return TimeUtil.parseTime(tx, TimeUtil.COMMON_FULL)
    
    @staticmethod
    def parseTime(pattern,tx=COMMON_FULL):
        return time.strptime(tx, pattern)
    
'''
XML工具类
'''    
class XmlUtil(object):
    
    @staticmethod
    def getAttrValue(node, attrname):
        return node.getAttribute(attrname) if node else ''

    @staticmethod
    def getSingleNodeValue(root, name):
        node = XmlUtil.getXmlNode(root,name)
        if node:
            return XmlUtil.getNodeValue(node[0])
        return None
    
    @staticmethod
    def getXmlNode(root,name):
        return root.getElementsByTagName(name) if root else []
    
    @staticmethod
    def getNodeValue(root, index = 0):
        if root and root.childNodes:
            return root.childNodes[index].nodeValue
        else:
            return ''
    
    @staticmethod
    def getRootNode(xml):
        doc = minidom.parseString(xml) 
        return doc.documentElement

'''
Http客户端请求工具类;
'''    
class HttpClient(object):

    '''
    发送GET请求
  data : dicts
    '''
    @staticmethod
    def exeGet(url):
        reload(sys)
        sys.setdefaultencoding('UTF-8')
        res = urllib2.urlopen(url)
        try:
            return res.read()
        except Exception as e:
            print(e)
            return None
        finally:
            res.close()
            
    '''
    发送POST请求
  data : dicts
    '''
    @staticmethod
    def exePost(url,data):
        reload(sys)
        sys.setdefaultencoding('UTF-8')
        res = urllib2.urlopen(url,data)
        try:
            return res.read()
        except Exception as e:
            print(e)
            return None
        finally:
            res.close()

'''
分页类；
'''
from django.core.paginator import Paginator,EmptyPage
class PaginatorHelper(object):

    '''
    分页数据：pageObjs
    页码：pageNum
    每页数量:pageSize
    '''
    @staticmethod
    def paginator_objs(pageObjs,pageNum,pageSize):
        paginator = Paginator(pageObjs, pageSize)
        try:
            page_objs = paginator.page(pageNum)
        except EmptyPage:
            page_objs = paginator.page(paginator.num_pages)
        page_nums = PaginatorHelper.get_pge_nums(pageNum,paginator.num_pages)#分页页号
        return {'page_objs':page_objs,'page_nums':page_nums}
    
    '''
    分页数据
    '''
    @staticmethod
    def paginator_objs_short(pageObjs,pageNum,pageSize):
        paginator = Paginator(pageObjs, pageSize)
        try:
            page_objs = paginator.page(pageNum)
        except EmptyPage:
            page_objs = paginator.page(paginator.num_pages)
        return {'page_objs':page_objs}
    
    '''
    为显示1-10页码使用
    '''
    @staticmethod
    def get_pge_nums(page,totalPage):
        if int(page) > totalPage:
            page = totalPage
        pn = totalPage#总页数
        page_nums = []
        if pn < 10:
            tmp = 0
            while tmp < pn:
                tmp += 1
                page_nums.append(tmp)
        else:
            vern = 1 #游标，在第三个位置处理
            if page:vern = int(page)
            if vern < 4:
                page_nums = [1,2,3,4,5,6,7,8,9]
            else:
                tmp = vern - 3
                while tmp < vern:
                    tmp += 1
                    page_nums.append(tmp)
                if vern + 6 < pn:
                    while tmp < vern + 6:
                        tmp += 1
                        page_nums.append(tmp)
                else:
                    cha = vern + 6 - pn
                    j = 0
                    while j < cha:
                        page_nums.insert(0, vern - 3 - j)
                        j += 1
                    while tmp < pn:
                        tmp += 1
                        page_nums.append(tmp)
        return page_nums

'''
Ajax请求，主要处理success
'''
class Ajax(object):
    '''
    渲染返回的json数据：jsonDict：dict类型参数
    '''
    @staticmethod
    def renderJson(jsonDict):
        jsonDict['success'] = True
        jsonObj = json.dumps(jsonDict)
        return HttpResponse(jsonObj,mimetype='application/javascript')

'''
邮件工具类
'''
class EmailHelper(object):
    '''
        发送邮件；
        param：dict
            template_name：模板名称；
            context：模板中使用到的参数；
            from_email：发送者；
            to_email：接收者
    '''
    @staticmethod
    def send_email(param):
        t = loader.get_template(param['template_name'])
        html_content = t.render(Context(param['context']))
        emsg = EmailMultiAlternatives(param['subject'], html_content, param['from_email'], param['to_email'])
        emsg.attach_alternative(html_content,'text/html')
        emsg.send()
    
    @staticmethod
    def picture(txt):
        p = re.compile(r'^[\w]+\.(png|jpg|jpeg|gif){1}$')
        return p.match(txt)

'''
正则表达式验证
'''
import re
class RegexValidator(object):
    '''
    简单的Email验证;
    如果是email，返回True；否则返回False
    '''
    @staticmethod
    def email(email):
        p = re.compile(r'^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]+$')
        return p.match(email)
    
    @staticmethod
    def picture(pname):
        p = re.compile(r'^[\w\W]*(.jpg|.png|.jpeg|.gif){1}$')
        return p.match(pname)
    
    @staticmethod
    def char_num(text):
        p = re.compile(r'^[a-zA-Z0-9]+$')
        return p.match(text)
    
    @staticmethod
    def is_empty(text):
        if text == None or text == '':
            return True
        else:
            p = re.compile(r'^\s*$')
            return p.match(text)
    
    @staticmethod
    def zh_char_num(text):
        p = re.compile(r'^[\u4E00-\u9FA5A-Za-z0-9]+$')
        return p.match(text)
    
    
'''
Cookie工具类
'''
class Cookie(object):
    
    c_login = '__c_persistent_login'#cookie的name
    s_login = '__s_persistent_login'#session的name
    
    '''
          设置记住密码（下次自动登录cookie和session）
    session的值会被保存到数据库中，django_session
    '''
    @staticmethod
    def set_persistent_login(request,response):
        max_age = settings.SESSION_COOKIE_AGE
        expires = cookie_date(time.time() + max_age)
        #cookie中加入用户自动登录标志, persistent_login:uuid
        value = uuid.uuid4()
        response.set_cookie(Cookie.c_login,value,max_age=max_age,expires=expires)
        request.session[Cookie.s_login] = value
        
    '''
          如果"remember me"，
    session中的值和cookie中的值进行比较，如果相等，那么返回True
    session中加值，是为了防止用户手动加cookie值
    '''
    @staticmethod
    def is_persistent_login(request):
        c = request.COOKIES.get(Cookie.c_login,None)
        if Cookie.s_login in request.session:
            s = request.session[Cookie.s_login]
        else:
            s = None
        if c and s and str(c) == str(s):
            return True
        else:
            return False
    
    '''
        删除 remember me
        删除cookie和session
    '''
    @staticmethod
    def delete_persistent_login(request,response):
        response.delete_cookie(Cookie.c_login)
        if Cookie.s_login in request.session:
            del request.session[Cookie.s_login]
    
    @staticmethod
    def get_session_key(request):
        return request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
    
    @staticmethod
    def set_cookie(request,response,key,value,expires):#expires:秒
        max_age = settings.SESSION_COOKIE_AGE
        expires = cookie_date(time.time() + expires)
        response.set_cookie(key,value,max_age=max_age,expires=expires)
    
    @staticmethod
    def get_cookie(request,key):
        return request.COOKIES.get(key,None)

'''
根据module_path : 模块路径
和class_name 类名,
'''
def get_class(module_path,class_name):
    __import__(module_path)#动态地导入模块
    m = sys.modules[module_path]#得到这个模块
    return getattr(m, class_name)

'''
获取class package
'''
def get_class_package_path(clazz):
    return re.subn('<|>|\'|class| ', '', str(clazz))[0]

'''
获取上传文件路径名
module_name：模块名称，static目录下 如 images/wxmng
file_name：文件名称，如 myfile.png
'''
def get_upload_filename(module_name,file_name):
    _media_url = settings.MEDIA_URL
    #文件路径
    path = os.path.split(file_name)[0]
    #文件扩展名
    ext = os.path.splitext(file_name)[1]
    #定义文件名，年月日时分秒随机数
    fn = time.strftime('%Y%m%d%H%M%S')
    fn = fn + '_%d' % random.randint(0,100)
    name = TimeUtil.formatSplitText() + '/' + path + fn + ext
    #文件目录
    full_path_name = _media_url + module_name + '/' + name
    d = os.path.dirname(full_path_name)
    if not os.path.exists(d):
        os.makedirs(d)
    return full_path_name

def get_upload_path(module_name):
    _media_url = settings.MEDIA_URL
    #定义文件名，年月日时分秒随机数
    fn = time.strftime('%Y%m%d%H%M%S')
    path = TimeUtil.formatSplitText() + '/' + fn
    #文件目录
    full_path = _media_url + module_name + '/' + path
    d = os.path.dirname(full_path)
    if not os.path.exists(d):
        os.makedirs(d)
    return full_path

'''
删除文件
'''
def remove_file(file_path):
    os.remove(file_path)


'''
判断是否是移动端
'''
def is_mobile(request):
    user_agent = request.META['HTTP_USER_AGENT']
    return re.compile(r'^.+(Android|iPhone OS).+$').match(user_agent)


#---------------------------------------------main test 
if __name__ == '__main__':
    print '''time = %s''' %TimeUtil.getIntTime()
    rep_xml = 'abc'
    rep_xml += 'def'
    print rep_xml
#     print RegexValidator.picture('a.png')
#     address = IPUtils.getIpAddress("218.94.126.122")
#     for a in address:
#         if a : print a
    data = {'button': [{'type': u'click', 'name': u'001', 'key': u'002'}, {'type': u'click', 'name': u'002', 'key': u'003'}, {'name': u'003', 'sub_button': [{'type': u'click', 'name': u'0031', 'key': u'aa81cebd-408d-4b07-9be0-cc3aadbfe28e'}, {'type': u'click', 'name': u'0032', 'key': u'5efd6893-1123-4389-b024-57daf2bad819'}]}]} 
    data = urllib.urlencode(data)
    print data
#     result = HttpClient.exePost('http://localhost:8000/test/json',data)
#     result = json.loads(result)
#     print result.keys()
#     print(result["access_token"])
   
