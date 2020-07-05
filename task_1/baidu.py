#-*- coding:utf-8 -*-
from task_1.start_end.write_file import write_file
from task_1.start_end.crawl_data import crawl_data
from task_1.combine_start_end import combine_start_end
from task_1.extract_function.basic_informatuon_extract import basic_information_extract
from task_1.extract_function.character_experience_extract import character_experience_extract
from task_1.extract_function.social_service_extract import social_service_extract
from task_1.extract_function.major_achievement_extract import major_achievement_extract
from task_1.extract_function.information_feedback import information_feedback
import re
def baidu_extract(name):
    source = '百度百科'
    #开始爬取数据
    baidu_response=crawl_data(name,source)
    # print("response")

    #百度基本信息提取
    delete = '\xa0|\n|<a.*?>|</a>|<sup.*?>|</sup>|<br/>|\uc720|\uc601|</em>展开</a>.*?</em>收起</a>|\xa9'
    option = '//div[@class="basic-info cmn-clearfix"]//dt[@class="basicInfo-item name"]/text()'
    value = '//div[@class="basic-info cmn-clearfix"]//dd[@class="basicInfo-item value"]/text()'
    div = '//div[contains(@class,"lemma-summary")]/div/text()'
    baidu_basic_information=basic_information_extract(baidu_response,delete,option,value,div)



    #百度人物经历提取
    form_delete = '<a.*?>|</a>|\xa0|<sup.*?>|</sup>|<div.*?>|</div>|<td>|\u25aa|\xa9|\n'
    text_delete = '<a.*?>|</a>|\xa0|<sup.*?>|</sup>|\u25aa|\xa9|\n|<b>|</b>'
    text_label = '//div[contains(@class,"para")]/text()'
    form_label = '//tr/text()'
    baidu_character_experience=character_experience_extract(baidu_response,source,form_delete,text_delete,form_label,text_label)


    #百度社会任职提取
    form_delete = '\u2082|<a.*?>|</a>|\xa0|<sup.*?>|</sup>|<div.*?>|</div>|<td.*?>|<td>|\u25aa|\xa9|\n'
    text_delete = '\u2082|<a.*?>|</a>|\xa0|<sup.*?>|</sup>|\u25aa|\xa9|\n'
    form_label = '//tr/text()'
    text_label = '//div/text()'
    baidu_social_service=social_service_extract(baidu_response,source,form_delete,text_delete,form_label,text_label)


    #百度主要成就信息提取
    form_delete = '\u2212|\u2217|\xf6|\ufb01|\xbe|\xee|\u30fb|<span.*?>|</span>|<td.*?>|<div.*?>|</div>|<th>|<a.*?>|</a>|\xa0|<sup.*?>|</sup>|\u25aa|\xa9|\n|\xa0|\r|\t|百度百科内容由网友共同编辑.*?立即前往>>|编辑|打开微信“扫一扫”即可将网页分享至朋友圈|登录|收藏|讨论|2019Baidu使用百度前必读\|百科协议\|隐私政策\|百度百科合作平台\||封禁查询与解封|投诉侵权信息|未通过词条申诉|举报不良信息|意见反馈|官方贴吧|在线客服|内容质疑|本人|规则|入门|成长任务|V百科往期回顾|图册|词条标签：|\n|进入技术百科.*?刘永才'
    text_delete = '\u2212|\u2217|\xf6|\ufb01|\xbe|\xee|\u30fb|<b>|</b>|<i>|</i>|<a.*?>|</a>|\xa0|<sup.*?>|</sup>|\u25aa|\xa9|\n|打开微信“扫一扫”即可将网页分享至朋友圈|登录|收藏|讨论|2019Baidu使用百度前必读\|百科协议\|隐私政策\|百度百科合作平台\||封禁查询与解封|投诉侵权信息|未通过词条申诉|举报不良信息|意见反馈|官方贴吧|在线客服|内容质疑|本人|规则|入门|成长任务|V百科往期回顾|图册|词条标签：|\n|rn|进入技术百科.*?刘永才'
    form_label = '//li[@class="row"]/text()|//tr/text()'
    text_label = '//div[contains(@class,"para")]/text()'
    baidu_major_achievement=major_achievement_extract(baidu_response,source,form_delete,text_delete,form_label,text_label)

    #information_feedback(name,source,baidu_character_experience,baidu_social_service,baidu_major_achievement)
    # write_file(name,source,baidu_basic_information,baidu_character_experience,baidu_social_service,baidu_major_achievement)
    return(baidu_basic_information + baidu_character_experience + baidu_social_service + baidu_major_achievement)

