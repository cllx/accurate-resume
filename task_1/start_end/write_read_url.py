 #-*- coding:utf-8 -*-
import os,sys 
import json
import re

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print("write_read_url.py:", parentdir)

def w_r_url(source,model,url={}):
    name_url = {}
    if model == 1:
        #1表示读取函数
        if source == '360百科':
            with open(os.path.join(parentdir,'start_end/bk360_name_url'), 'r', encoding='utf-8') as f:
                name_url = f.read()
            if name_url.startswith(u'\ufeff'):
                #忽略掉BOM字符
                name_url = name_url.encode('utf8')[3:].decode('utf8')
            name_url = re.sub('\'','"',name_url)
            name_url = json.loads(name_url, strict=False)
        elif source == '搜狗百科':
            with open(os.path.join(parentdir,'start_end/sougou_name_url'), 'r', encoding='utf-8') as f:
                name_url = f.read()
            if name_url.startswith(u'\ufeff'):
                #忽略掉BOM字符
                name_url = name_url.encode('utf8')[3:].decode('utf8')
            name_url = re.sub('\'', '"', name_url)
            name_url = json.loads(name_url, strict=False)
        elif source == '互动百科':
            with open(os.path.join(parentdir,'start_end/hudong_name_url'), 'r', encoding='utf-8') as f:
                name_url = f.read()
            if name_url.startswith(u'\ufeff'):
                #忽略掉BOM字符
                name_url = name_url.encode('utf8')[3:].decode('utf8')
            name_url = re.sub('\'', '"', name_url)
            name_url = json.loads(name_url, strict=False)
        elif source == '百度百科':
            with open(os.path.join(parentdir,'start_end/baidu_name_url'), 'r', encoding='utf-8') as f:
                name_url = f.read()
            if name_url.startswith(u'\ufeff'):
                #忽略掉BOM字符
                name_url = name_url.encode('utf8')[3:].decode('utf8')
            name_url = re.sub('\'', '"', name_url)
            name_url = json.loads(name_url, strict=False)
        return (name_url)
    if model == 2:
        #表示写入函数
        if source == '360百科':
            with open(os.path.join(parentdir,'start_end/bk360_name_url'), 'a+', encoding='utf-8') as f:
                f.truncate(0)
                f.write(str(url))
        elif source == '搜狗百科':
            with open(os.path.join(parentdir,'start_end/sougou_name_url'), 'a+', encoding='utf-8') as f:
                f.truncate(0)
                f.write(str(url))

