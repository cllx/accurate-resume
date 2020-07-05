 #-*- coding:utf-8 -*-
from baidu import baidu_extract
from sougou import sougou_extract
from hudong import hudong_extract
from bk360 import bk360_extract
import requests
from lxml import etree
import re
import json

# name = input('请输入要提取的院士姓名：\n')
name = "方滨兴"
a=baidu_extract(name)
# print("baidu:\n",a)
# b=sougou_extract(name)
# c=hudong_extract(name)
# d=bk360_extract(name)
# headers = {'user-agent': 'my-app/0.0.1'}
# url = 'http://www.cae.cn/cae/html/main/col48/column_48_1.html'
# response = requests.get(url,headers = headers)
# response.encoding = 'utf-8'
# response = re.sub('<a.*?>|</a>|\u2022|\(女\)', '', response.text)
# selector = etree.HTML(response)
# academician_list = selector.xpath('//li[@class="name_list"]/text()')
# a = academician_list
# academician_list = list(set(academician_list)) #去重
# academician_list.sort(key=a.index) #保持顺序不变
# name = academician_list

# with open('academician_name.txt', 'r', encoding='utf-8') as f:
#      name = f.readlines()# first_title
# for i in range(len(name)):
#      name[i] = re.sub('\n','',name[i])
# print(name)
# delete = ['陈学东','何琳','侯晓','李钊',
#           '李骏','刘永才','邱志明','孙聪',
#           '张军','王振国','王玉明','黄文虎',
#           '李鸿志','李明','王永志','武胜']
# a = []
# for i in range(len(name)):
#      if name[i] not in delete:
#           a.append(name[i])
# name = a

# name = ['方滨兴','潘云鹤','邬贺铨','杨小牛','张尧学','黄先祥','黄庆学','冯煜芳',
#          '甘晓华','路甬祥','马伟明','金东寒','邓宗全','路甬祥','林忠钦','李德群',
#          '朱能鸿','杨凤田','唐长红','朱英富','王华明','陈一坚','陈予恕','范本尧',
#          '孟执中','李鹤林','梁晋才','胡正寰','范本尧','郭重庆','张贵田','王兴治',
#         '王浚','高文','陈杰','余少华','吴澄','何德全','金怡濂','陆建勋','张明高',
#         '王小谟','王越','丁文江','李卫','钟山','陈祥宝','李仲平','潘复生','吴锋',
#         '周廉','张耀明','陈清如','徐匡迪','张文海','李根生','邓建军','彭苏萍','唐立',
#         '孙金声','李阳','王国法','于润沧','崔愷','李建成','任南琪','张建民','王浩',
#         '王超','王光远','王景全','王小东','吴丰昌','谢剑平','周翔','张懿','李玉','石玉林',
#         '丁健','丛斌','李松','马丁','徐建国','洪涛','王锐','朱晓东','周建平','孙聪','张军']
# baidu_extract(name[88])
# bk360_extract(name[88])
# hudong_extract(name[88])
# sougou_extract(name[88])
# sougou_extract(name[16])

# name = ['陈学东','何琳','侯晓','李钊',
#           '李骏','刘永才','邱志明','孙聪',
#           '张军','王振国','王玉明','黄文虎',
#           '李鸿志','李明','王永志','武胜']
