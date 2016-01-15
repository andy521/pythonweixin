
#coding=utf-8
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = patterns('pythonweixin.views',
                       url(r'^$','homepage'),#首页
)

#引入静态资源文件
urlpatterns += staticfiles_urlpatterns()

#wxcms
urlpatterns += patterns('',
      url(r'^wxcms/', include('wxcms.urls')),
)

#wxapi
urlpatterns += patterns('',
      url(r'^wxapi/', include('wxapi.urls')),
)

