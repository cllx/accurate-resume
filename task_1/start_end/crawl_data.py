#-*- coding:utf-8 -*-
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from task_1.start_end.write_read_url import w_r_url
def crawl_data(name,source):
    headers = {'user-agent': 'my-app/0.0.1'}  # 简单地掩饰身份
    source_url = {'百度百科':'https://baike.baidu.com/item/',
                  '互动百科': 'http://www.baike.com/wiki/',
                  '360百科': 'https://baike.so.com/',
                  '搜狗百科': 'https://baike.sogou.com/'}
    source_id = {'百度百科':'',
                 '互动百科':'',
                 '360百科':'J-search-word',
                 '搜狗百科':'searchText'}  #使用selenium时用来定位的id
    name_url = w_r_url(source, 1)  # 从文本中读出已经码下来的搜狗或者bk360的网页地址，还有重名的需要指定网址的院士
    #这两个百科不能直接通过名字获取链接
    if name in name_url:
        #如果链接已经码下来了，就直接直接使用链接访问
        # print(name_url[name])
        response = requests.get(name_url[name], headers=headers)
    elif source_id[source] != '':
        #如果字典中的values为空，说明还没码下来，并且通过source_id的value值来判定是否需要借助selenium来获取网页源代码
        path = './chromedriver_win32/chromedriver.exe'
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(executable_path=path,chrome_options=chrome_options)
        # driver = webdriver.Chrome(executable_path=path)
        #从if判断到这里为止都是为了让浏览器不弹出来
        driver.get(source_url[source])
        a = name
        name = name + '\n'
        driver.find_element_by_id(source_id[source]).send_keys(name)
        time.sleep(5)
        response = requests.get(driver.current_url, headers=headers)
        print(driver.current_url)
        #把获取网页链接码下来，便于下次复用
        name_url.update({a:driver.current_url})
        w_r_url(source,2,name_url)
    else:
    #不需要使用selenium
        url = source_url[source] + '{name}'
        response = requests.get(url.format(name=name), headers=headers)
    response.encoding = 'utf-8'
    return response.text
