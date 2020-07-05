#-*- coding:utf-8 -*-
import re
from lxml import etree
from task_1.combine_start_end import combine_start_end
def character_experience_extract(response,source,form_delete,text_delete,form_label,text_label):
    character_experience = []
    similar_word = ['人物经历', '人物履历', '个人履历','生平简介','人物生平','学历经历',
                    '个人简介','个人简历', '个人经历',  '人物生平','人物介绍','履历','任职经历',
                    '生平','经历','人物简介','院士简历','院士简介','个人信息','简历','基本信息',
                    '基本情况','人物概述','参选院士','教育背景','科研经历','成长经历',
                    '主要学习及工作经历','<h2.*?>简介','人物事迹','事迹','主要经历','生平介绍',
                    '人物年表','1932.9','个人年表','履历年表','个人资料','职称','国外经历','学历',
                    '教育履历','钮新强','受教育情况','生平概况','事迹','基本介绍','求学简历',
                    '人物故事','人物资料','农科院研究员','学习生涯','教育经历','巴德年人物简历',
                    '上海长征医院皮肤科主任医师','介绍','生平简介','事业发展','大事记']
    baidu_end = '</h2>.*?<h2'
    hudong_end = '<span class="f18">.*?<h2'
    bk360_end = '</b></h2>.*?<h2>'
    bk360_start = '<b class=title>'
    if source == '百度百科':
        start_end = combine_start_end(similar_word,baidu_end)
    elif source == '互动百科':
        start_end = combine_start_end(similar_word,hudong_end)
    else:
        start_end = combine_start_end(similar_word,bk360_end,bk360_start)
    for i in range(len(start_end)):
        response = re.sub(text_delete, '', response)
        character_experience_html = re.search(str(start_end[i]),response,re.S)
        #print (character_experience_html)
        if character_experience_html != None:
            #如果character_experience不为空，提取到了信息，进行进一步处理
            a = character_experience_html.group()  # 用a记录原始数据，以后会用到
            character_experience_form = re.sub(form_delete, '', character_experience_html.group())
            character_experience_form = re.sub('</td>|</th>', ' ', character_experience_form)
            selector = etree.HTML(character_experience_form)
            character_experience_form = selector.xpath(form_label)
            if character_experience_form != []:
            # 如果是表格形式，就执行下面代码
                for i in range(len(character_experience_form)):
                    character_experience_form[i] = re.sub('\n|\xa0|\r|\ ', '', character_experience_form[i])
                # 去掉链表里面的空项
                character_experience_form = list(filter(None, character_experience_form))
            selector = etree.HTML(a)
            character_experience_text = selector.xpath(text_label)
            for i in range(len(character_experience_text)):
                #遍历链表，整理提取出来的内容
                character_experience_text[i] = re.sub('\n|\xa0| ','',character_experience_text[i])
            character_experience_text = list(filter(None, character_experience_text))  # 去掉链表里面的空项
            character_experience = character_experience_form + character_experience_text + character_experience
            a = character_experience
            character_experience = list(set(character_experience))  # 去重
            character_experience.sort(key=a.index)  # 保持顺序不变

    for i in range(len(character_experience)):
        character_experience[i] = re.sub('打开微信“扫一扫”即可将网页分享至朋友圈|登录|收藏|讨论|2019Baidu使用百度前必读\|百科协议\|隐私政策\|百度百科合作平台\||封禁查询与解封|投诉侵权信息|未通过词条申诉|举报不良信息|意见反馈|官方贴吧|在线客服|内容质疑|本人|规则|入门|成长任务|V百科往期回顾|图册|词条标签：|编辑','',character_experience[i])
        character_experience[i] = re.sub('u2014','-', character_experience[i])
    # 去掉链表里面的空项
    character_experience = list(filter(None, character_experience))
    character_experience.insert(0,'人物经历')
    # print(character_experience)
    return(character_experience)