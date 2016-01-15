#coding=utf-8
'''
Created on Oct 11, 2013
@author: brain
中间件：SessionMiddleware的扩展
主要处理，记住 用户名、密码的用户，下次直接登录；
'''

import time
from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date
from django.utils.importlib import import_module
from core.utils import Cookie

class RfSessionMiddleware(object):
    def process_request(self, request):
        engine = import_module(settings.SESSION_ENGINE)
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        request.session = engine.SessionStore(session_key)

    def process_response(self, request, response):
        """
        If request.session was modified, or if the configuration is to save the
        session every time, save the changes and set a session cookie.
        """
        try:
            accessed = request.session.accessed
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if accessed:
                patch_vary_headers(response, ('Cookie',))
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    self._process_persistent_login(request)#处理登陆时："remember me"
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = cookie_date(expires_time)
                    
                #Save the session data and refresh the client cookie.
                request.session.save()
                response.set_cookie(settings.SESSION_COOKIE_NAME,
                        request.session.session_key, max_age=max_age,
                        expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                        path=settings.SESSION_COOKIE_PATH,
                        secure=settings.SESSION_COOKIE_SECURE or None,
                        httponly=settings.SESSION_COOKIE_HTTPONLY or None)
        return response

    '''
    判断用户是否选中"remember me",通过改变expiry 来实现
    如果没有，那么session的失效时间，就使用SESSION_TIMEOUT
    否则，使用django的默认配置；
    '''
    def _process_persistent_login(self,request):
        if settings.SESSION_TIMEOUT and request.user.is_authenticated():#用户已经登录
            if Cookie.is_persistent_login(request):
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            else:
                request.session.set_expiry(settings.SESSION_TIMEOUT)
    