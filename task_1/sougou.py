#-*- coding:utf-8 -*-
from lxml import etree
import re
import json
from task_1.start_end.write_file import write_file
from task_1.start_end.crawl_data import crawl_data
from task_1.extract_function.basic_informatuon_extract import basic_information_extract
from task_1.extract_function.information_feedback import information_feedback
def sougou_information_extract(sougou_response,title):
    sougou_information = []
    source_delete_1 = '<a.*?>|</a>|\\\\|\u25aa|\xa0'
    source_delete_2 = '\ue011|\ufb01|\ue003|\ue004|\xee|\ue584|</sup>|<sup>|</a>|<img.*?/>|<td.*?>|<th.*?>|<table.*?>|\u25aa|<tr.*?>|\xa0|</a>|<br />|sizset.*?sizcache="2"|sizcache.*?sizset="35"|<mining science.*?>|sizset=".*?".*?".*?"|<dl id=.*?>'
    match_label = '{"paragraph".*?}]}'
    sougou = re.sub(source_delete_1, '', sougou_response)
    sougou = re.sub(source_delete_2, '', sougou)
    data = re.search(match_label, sougou)
    if data != None:
        # print (data.group())
        # data = re.sub('</sup>|<sup>|</a>|<img.*?/>|<td.*?>|<th.*?>|<table.*?>|\u25aa|<tr.*?>|\xa0','',data.group())
        data = json.loads(data.group(), strict=False)
        # print(data)
        for i in data['paragraph']:
            i['title'] = re.sub(' ','',i['title'])
            if i['title'] in title:
                content = i.get('content', '不存在！')
                if content != '不存在！':
                    #如果标签所对应的内容存在，则提取其内容
                    # print(i)
                    i['content'] = re.sub('</th>',' ',i['content'])
                    i['content'] = re.sub('</td>', ' ', i['content'])
                    i['content'] = re.sub('</tr>', '<td>', i['content'])
                    selector = etree.HTML(i['content'])
                    median = selector.xpath('//b/text()|//p/text()|//li/text()')
                    sougou_information = sougou_information + median
                    median = selector.xpath('//td/text()')
                    sougou_information = sougou_information + median
        k = []
        for i in range(len(sougou_information)):
            j = re.sub('u2014','-',sougou_information[i])
            j = re.sub('u201c|u201d|rn|\xbe|\ue584|\xee', '', j)
            if j == ' ':
                #把只有空格的项中的空格给去掉，方便之后处理
                j = re.sub(' ', '', j)
            k.append(j)
        sougou_information = k
        sougou_information = list(filter(None, sougou_information))
        # print(sougou_information)
    return (sougou_information)

def sougou_extract(name):
    #开始爬取数据
    source = '搜狗百科'
    sougou_response = crawl_data(name,source)


    # #搜狗基本信息提取
    sougou = re.sub('<a.*?>|</a>|\\\\|\u25aa', '', sougou_response)
    sougou = re.sub('</a>|<br />|\xbe', '', sougou)
    options = '//table[@class="abstract_tbl"]//td[@class="abstract_list_wrap"]//tr/th/text()'
    # values = '//table[@class="abstract_tbl"]//td[@class="abstract_list_wrap"]//tr/td/text()'
    values = '//table[@class="abstract_tbl"]//td[@class="abstract_list_wrap"]//tr/td//div[@class="base-info-card-value"]/text()'
    # delete = '</a>|<br />'
    delete = '</ a>|<br />|\n'
    sougou_basic_information = basic_information_extract(sougou,delete,options,values)



    # #搜狗人物经历
    title = ['人物经历', '人物履历', '人生经历', '人物简介', '个人履历', '生平简介',
             '简介','基本内容','学历经历','任职经历','个人简历','简历','人物介绍',
             '学习经历','人物背景','主要经历','人物生平','主要经历','个人信息',
             '中国工程院院士','主要学历','工作经历','基本信息','基本介绍','个人简介','生平',
             '人物名片','个人资料','主要经历','本人简介','生平介绍','人物概述','周勤之'
             '参选院士','学历','个人经历','科研经历','履历','人物简历','概述','教育经历',
             '论文著述','研究荣誉','人物年表','主要学习及工作经历','邬江兴','介绍','人物事迹',
             '人物经历','翁宇庆','学习简历','工作简介','经历','中国工程院院士、材料化学专家',
             '项目主持','个人年表','学术论著','教授','公司高管','院士简介','学术','基本资料',
             '周守为-简介','周守为-经历','生平详述','求学时期','余贻鑫','履历年表','个人基本简介','求学经历','石油勘探','转战东营',
             '研究生培养','主要学术成就','职称','国内经历','国外经历','详细介绍','教育工作经历',
             '个人介绍','专家简介','经历','葛修润','院士简历','沙庆林','教学及研究经历','生平介绍',
             '国内外学术经历、荣誉、合作等:','名片','相关介绍','汤鸿霄','基本经历','科研经历',
             '人物资料','研究经历','事业发展','生平概述','基本简介','主要履历']
    sougou_character_experience = sougou_information_extract(sougou_response,title)
    sougou_character_experience.insert(0,'人物经历')



    #搜狗社会任职
    title = ['社会任职', '任免信息', '学术兼职', '重要职务',
             '学术职务', '社会兼职', '担任职务', '主要职位',
             '兼任职务', '其他兼职', '主要兼职', '学术任职',
             '社会职务','工作简历','工作历程','个人简历',
             '社会工作','双聘单位','任职情况','曾任职务',
             '现任职务','学术或专业团体任职','职业生涯',
             '工作经历','职称简历','任职简历','受聘单位',
             '学习工作','工作履历','人物职务','社会关系',
             '兼职情况','现任职位','工作时期','薛禹胜.学术兼职',
             '主要职务','行政职务','科研职务','详细介绍',
             '职务任免','现任：','曾任：','学会','期刊','高校',
             '团体任职','高校兼职','专家简介','任职信息',
             '国内任职','国际任职','教育与学术兼职','学术任职:',
             '任职介绍','科学技术奖获奖项目','任编辑情况','从业经历',
             '国内外学术兼职','任职经历','工作历程','职业履历','职务信息',
             '主要任职','兼职','历任职务','教育贡献','职位任免']
    sougou_social_service = sougou_information_extract(sougou_response,title)
    sougou_social_service.insert(0,'社会任职')



    #搜狗主要成就
    title = ['科研成就','人才培养','荣誉表彰','个人成果','获的奖项','相关研究','研究方向','代表论文',
             '论文专著','研究领域','研究成果','主要成就','所获荣誉','主要贡献','荣誉记录','荣誉称号',
             '理论成果','科研成果','成就荣誉','成就与荣誉','著名专著','成就','主持项目','论文著作','科技奖励',
             '论著成果','获奖记录','研究方向','参选院士','曾获荣誉','学术研究','人物荣誉','综述','黄先祥',
             '主要成果','科研项目','专业成就','获得荣誉','科研简介','获奖荣誉','科学意义','教研成果','双聘院士',
             '科研工作','荣誉成就','个人称誉','科研方向','主要研究领域','所获奖励','荣获奖励','贡献成就',
             '人物著作','个人成就','承担项目','荣誉成果','科学中国人(2009)年度人物杨绍卿','荣誉','论文',
             '科技奖项','综合奖项','发明专利','代表性成果','科学专著','突出贡献','学术著作','个人荣誉',
             '国防成就','主要著作','撰写论文','主要成绩','科技成就','主要论著','敏事慎行成方圆',
             '放眼世界攀高峰','荣誉与工作单位','著作','教学方面','科研方面','主要成就和贡献有','专业著作',
             '会议论文','期刊论文','科技贡献','科技成果','主要业绩','人物作品','学术成果','核潜艇','深潜实验',
             '人物成就','人物影响','主要学术著作','成就及荣誉','贡献','人才培育','课题研究','代表性论文','代表性著作',
             '学术成就','发展','起步','论著','人物贡献','科学研究','科学成果','最后攻关','内容','成果',
             '称呼段教授','简介','后记','学术领域','人物研究','学术文章','生平经历','主要荣誉','教学成就',
             '专著','社会贡献','论文与专著','获奖与专利','主要研究方向','学术贡献','科研奖励','豪情在胸',
             '获奖与成果','科研贡献','代表著作','主要论文','学术荣誉','主要贡献及个人荣誉','概况','事迹',
             '学术经历','软件工程','项目荣誉','抗静电、抗电磁脉冲技术连获大奖','评价','中国微波遥感权威',
             '国防贡献','个人成就1','个人成就2','个人其它信息','获奖情况','个人专著','研究成就','技术考察',
             '开创新领域','发展高新技术','退居二线','下一代培养','科研概况','荣誉获奖','研究课题','获得奖项',
             '著作及论文','科研项目和成果','专利','工作成果','宋健行星','人物评价','科学生涯','研究方向、论著成果',
             '学术论文','社会评价','个人著述','个人作品','研究成绩','获奖成果','独立董事','担任顾问','主要作品',
             '成就之路','科技企业','获奖','研究课题及成就','所获殊荣','教学成果','研究项目','教学科研','研究课题及成就',
             '研究项目','社会影响','兼职','成果荣誉','主要工作及成果','发表联名论文','所获成就','主要殊荣',
             '硕果累累奋斗不息','研究工作','科研成果及学术成就','个人贡献','科研信息','所获成绩','工作简介',
             '奖项荣誉','教育教学','1从事领域','主要获得荣誉','代表作品','获奖及论著','万元熙','孙承纬','科研获奖',
             '科研情况','主要工作及成就','社会评价及荣誉','人物著作','获奖成果（国家科学进步奖）','人物业绩',
             '获得的主要科研成果','主持的主要科研项目','教育科研','院士简介','勘探进展','出版论著','周守为-著作',
             '周守为-科研成果','主要工作与获得的成果','出版专著','发表论文','薛禹胜.荣誉称号',
             '其它重要奖项','国家级科技奖项','薛禹胜.学术成果','工作成就','作品','技改应用','卓越成绩',
             '工作阶段','主要学术成果','成果鉴定','主要成就与奖项','个人成就与贡献','学术观点','作品发表',
             '分离膜研制','学术奖励','个人获奖情况','成果获奖情况','主持工作','取得成绩','贡献荣誉',
             '教学工作','科技项目','学术项目','主要研究','专业及成果','社会评价','发表文章','贡献','学术成就',
             '部分论文','院士重要科学成就概述','主要论著成果','荣誉及获奖','国际交流','事迹',
             '技术成就','规划实践','学术交流','省、部级','国家级','主要获奖成果','承担主要国家项目',
             '主要研究成果','主要科技奖励','主要研究项目','国内外获得的荣誉：','人物获奖','个人殊荣',
             '教材建设','主要研究内容与方向','相关','当选院士','国家奖项','作品荣誉','研究领域及成果',
             '获得荣誉和奖励','主要研究领域及成果','工作成绩','获得奖励','主攻方向','荣誉与奖项','荣誉奖项',
             '获得奖励','成就贡献','取得成果','院士','奋斗历程','专业影响','研究贡献','相关成果','科研业绩',
             '首项研究','束怀瑞','汪懋华','医学成就','科研概述','个人情况','成果介绍','技术成果','学术及科研成果',
             '成绩奖项','公益慈善','财富排名','获得的奖励','人物信息','工作内容','主要从事','取得成就','论文及著作',
             '擅长','主要奖励','学术地位','荣誉及成果','主要科学技术成就','专业特长','简述','详尽','主要工作成绩','团体兼职',
             '主要事迹','取得荣誉','马大猷声学奖']
    a = title
    title = list(set(title))  # 去重
    title.sort(key=a.index)  # 保持顺序不变
    sougou_major_achievement = sougou_information_extract(sougou_response,title)
    sougou_major_achievement.insert(0,'主要成就')



    #information_feedback(name,source,sougou_character_experience,sougou_social_service,sougou_major_achievement)
    # write_file(name,source,sougou_basic_information,sougou_character_experience,sougou_social_service,sougou_major_achievement)
    return (sougou_basic_information+sougou_character_experience+sougou_social_service+sougou_major_achievement)