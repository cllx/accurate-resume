#-*- coding:utf-8 -*-
import re
from lxml import etree
from task_1.combine_start_end import combine_start_end
def social_service_extract(response,source,form_delete,text_delete,form_label,text_label,model=1):
    social_service = []
    if model == 1:
        #模式为1，即按照正常的方法定位标签
        similar_word = ['社会任职', '学术兼职', '任免信息','学术职务','社会兼职','主要职位',
                        '兼任职务','担任职务','任职','职务','兼职','工作','履新信息','科研经历',
                        '个人信息','学术或专业团体任职','从事专业','任职情况','历任职务',
                        '中科院院士','任职经历','职业生涯','主要工作经历','职务信息','工作经历',
                        '受聘单位','工作履历','学术兼职','曾任职务','社会关系','专家组专','任职简历',
                        '受聘情况','行政职务','科研职务','职称和职务','职务任免','工作简历','任职信息',
                        '国际职务','从业经历','兼职情况','工作历程','职业履历','任教情况','职务一览',
                        '曾任兼职']
        baidu_end = '</h2>.*?<h2'
        hudong_end = '<span class="f18">.*?<h2'
        bk360_end = '</b></h2>.*?<h2>'
        if source == '百度百科':
            start_end = combine_start_end(similar_word, baidu_end)
        elif source == '互动百科':
            start_end = combine_start_end(similar_word, hudong_end)
        else:
            start_end = combine_start_end(similar_word, bk360_end)
    elif model == 2:
        #模式为2，说明该标签为最后一个，并且无法正常定位，需要使用特殊标签
        similar_word = ['社会兼职']
        baidu_end = ''
        hudong_end = '<span class="f18">.*?class="clear"'
        bk360_end = ''
        if source == '百度百科':
            start_end = combine_start_end(similar_word, baidu_end)
        elif source == '互动百科':
            start_end = combine_start_end(similar_word, hudong_end)
        else:
            start_end = combine_start_end(similar_word, bk360_end)

    for i in range(len(start_end)):
        social_service_html = re.search(str(start_end[i]),response,re.S)
        if social_service_html != None:
            #如果不为空，说明提取到信息，进行下一步处理
            a = social_service_html.group() #用a记录原始数据，以后会用到
            social_service_initiall =re.sub(form_delete,'',social_service_html.group())
            selector = etree.HTML(social_service_initiall)
            social_service_form = selector.xpath(form_label)
            if social_service_form != []:
            #如果是表格形式，就执行下面代码
                for i in range(len(social_service_form)):
                    social_service_form[i] = re.sub('\n|\xa0|\r|\ ','',social_service_form[i])
                # 去掉链表里面的空项
                social_service_form = list(filter(None, social_service_form))
            # 提取非表格信息
            a = re.sub(text_delete,'',a)
            selector = etree.HTML(a)
            social_service_text = selector.xpath(text_label)
            for i in range(len(social_service_text)):
                #去除无用标签
                social_service_text[i] = re.sub('\n|\xa0|\r| ','',social_service_text[i])
            social_service_initiall = social_service_text + social_service_form
            social_service = social_service + social_service_initiall
            a = social_service
            social_service = list(set(social_service))  # 去重
            social_service.sort(key=a.index)  # 保持顺序不变
    if social_service == []:
        #如果social_service没有那内容,提醒用户
        print('请在similar_world中加入正确的标签或者检查网页中有没有对应内容')
    for i in range(len(social_service)):
        social_service[i] = re.sub('打开微信“扫一扫”即可将网页分享至朋友圈|登录|收藏|讨论|2019Baidu使用百度前必读\|百科协议\|隐私政策\|百度百科合作平台\||封禁查询与解封|投诉侵权信息|未通过词条申诉|举报不良信息|意见反馈|官方贴吧|在线客服|内容质疑|本人|规则|入门|成长任务|V百科往期回顾|图册|词条标签：|编辑','',social_service[i])
    # 去掉链表里面的空项
    social_service = list(filter(None, social_service))
    social_service.insert(0,'社会任职')
    # print (social_service)
    return(social_service)