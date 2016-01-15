#coding=utf-8

from django.shortcuts import render_to_response
from django.template import RequestContext


'''
首页
'''
def homepage(request):
    c = {}
    
    return render_to_response("index.html", c,context_instance=RequestContext(request))

    