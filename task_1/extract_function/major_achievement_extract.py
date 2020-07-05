#-*- coding:utf-8 -*-
import re
from lxml import etree
from task_1.combine_start_end import combine_start_end
def major_achievement_extract(response,source,form_delete,text_delete,form_label,text_label):
    similar_word = ['主要成就', '研究成果', '所获荣誉', '理论成果',
                    '研究领域', '科研成果', '个人作品', '成就荣誉',
                    '工作成绩', '获得荣誉', '成就及荣誉', '科研成就',
                    '主持项目', '论文与著作', '科技奖励', '科学研究',
                    '人物荣誉', '参选院士', '曾获荣誉', '学术研究',
                    '获奖', '科研项目', '主要成果', '成就与荣誉', '著名专著',
                    '科研情况', '研究方向', '人物贡献', '成就', '主要贡献',
                    '获奖记录', '人物事件', '个人成就','工作分工','人物著作',
                    '人物成就','贡献','科研简介','荣誉','科学意义','双聘院士',
                    '科研工作','论文著作','称誉','科研方向','奖励','成果','项目',
                    '最美教师','著作','学术简介','研究生涯','主要成绩','敏事慎行成方圆',
                    '放眼世界攀高峰','奖项','专著','优秀研发成果','主要论著','贡献','影响'
                    ,'应用研发','人物影响','学术著作','教学方面','科研方面','奖项','论文',
                    '主要业绩','人物作品','社会活动','人物影响','简介','特点','成就历程',
                    '研制工作','课题研究','科研历程','成果展示','工程研究','学术领域','人物研究',
                    '获奖情况','荣誉奖励','发明专利','研究历史','豪情在胸','研究成绩','学术科研',
                    '代表论著','主要作品','软件工程师','人物详情','突出贡献','个人其它信息','研究课题',
                    '宋健行星','人物评价','科学生涯','潘君骅','获奖记录','著作简介','代表作','个人著述',
                    '社会评价','独立董事','奠基人','成就之路','所获殊荣','职位','论文作品','荣誉表彰',
                    '参编教材','研究工作','学术荣誉','科研信息','项目主持','荣誉称号','学术论著','教学业绩',
                    '教育科研','贡献简述','代表作品','获奖及论著','个人风采','获奖成果（国家科学进步奖）',
                    '人物业绩','应用','科技攻关','勘探进展','出版论著','卓越成绩','先进事迹','学术观点',
                    '辉煌业绩','作品发表','分离膜研制','科研领域','学术奖励','获奖情况','个人成绩',
                    '社会评价','研究发现','当选院士','硕果累累 无私奉献','于振文人民网新闻','奋斗历程',
                    '人才培养','科研成果效益','科技获奖','临床经验','学术思想','工作内容','主要从事','中医现代化',
                    '团队业绩','从事工作','专业特长','科研奖励','教学工作','重大荣誉','马大猷声学奖']
    baidu_end = '</h2>.*?<h2'
    hudong_end = '<span class="f18">.*?<h2'
    bk360_end = '</b></h2>.*?<h2>'
    if source == '百度百科':
        start_end = combine_start_end(similar_word, baidu_end)
    elif source == '互动百科':
        start_end = combine_start_end(similar_word, hudong_end)
    else:
        start_end = combine_start_end(similar_word, bk360_end)

    a = start_end
    start_end = list(set(start_end))  # 去重
    start_end.sort(key=a.index)  # 保持顺序不变
    major_achievement = []
    for i in range(len(start_end)):
        major_achievement_html = re.search(str(start_end[i]), response, re.S)

        if major_achievement_html != None:
        # 如果不为空，说明这个人简历中有这一块内容
            major_achievement_html = re.sub('\u25aa|进入技术百科.*?周守为|<i>|</i>', '', major_achievement_html.group(), flags=re.S | re.M)
            a = major_achievement_html  # 用a记录原始数据，以后会用到
            major_achievement_initiall = re.sub(form_delete, '', major_achievement_html,flags=re.S|re.M)
            major_achievement_initiall = re.sub('</td>|</th>', '-', major_achievement_initiall)

            selector = etree.HTML(major_achievement_initiall)
            major_achievement_1 = selector.xpath(form_label)
            if major_achievement_1 != []:
            #如果该变量不为空，说明有表格数据，按表格的形式提取数据
                for i in range(len(major_achievement_1)):
                    major_achievement_1[i] = re.sub(form_delete,'',major_achievement_1[i])
                    major_achievement_1[i] = re.sub(' ', '', major_achievement_1[i])


            a = re.sub(text_delete,'',a,flags=re.S|re.M)
            selector = etree.HTML(a)
            major_achievement_2 = selector.xpath(text_label)#提取非表格信息
            for i in range(len(major_achievement_2)):
            #去除一些无用的信息
                major_achievement_2[i] = re.sub(text_delete,'',major_achievement_2[i])
            major_achievement_2=list(filter(None,major_achievement_2))
            major_achievement_initiall = major_achievement_2 + major_achievement_1
            major_achievement = major_achievement + major_achievement_initiall
            a = major_achievement
            major_achievement = list(set(major_achievement))  # 去重
            major_achievement.sort(key=a.index)  # 保持顺序不变
    if major_achievement == []:
        #如果为空，则没有社会任职这一消息
        print('请在similar_world中加入正确的标签或者检查网页中有没有对应内容')
    if source == '互动百科':
        for i in range(len(major_achievement)):
            major_achievement[i] = re.sub(' |\n','',major_achievement[i],flags=re.S|re.M)
    major_achievement = list(filter(None, major_achievement))
    major_achievement.insert(0,'主要成就')
    # print(major_achievement)
    return(major_achievement)
