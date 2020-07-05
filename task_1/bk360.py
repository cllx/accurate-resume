#-*- coding:utf-8 -*-
from task_1.start_end.write_file import write_file
from task_1.start_end.crawl_data import crawl_data
from task_1.combine_start_end import combine_start_end
from task_1.extract_function.basic_informatuon_extract import basic_information_extract
from task_1.extract_function.character_experience_extract import character_experience_extract
from task_1.extract_function.social_service_extract import social_service_extract
from task_1.extract_function.major_achievement_extract import major_achievement_extract
from task_1.extract_function.information_feedback import information_feedback
def bk360_extract(name):
    source = '360百科'
    #开始爬取数据
    bk360_response = crawl_data(name,source)


    #360基本信息提取
    delete = '\u200b|\xa0|\n|<a.*?>|</a>|<sup.*?>|</sup>|<img.*?>|<br />'
    option = '//div[@class="card-list-box"]//p[contains(@class,"cardlist-name")]/text()'
    value = '//div[@class="card-list-box"]//p[contains(@class,"cardlist-value")]/text()'
    bk360_basic_information = basic_information_extract(bk360_response, delete, option, value)


    #360人物经历信息提取
    form_delete = '<a.*?>|</a>|\xa0|<sup.*?>|</sup>|<div.*?>|</div>|<td.*?>|<td>|\u200b|/ |/n|<sub.*?>|</sub>|<span.*?>|</span>|<strong>|</strong>'
    text_delete = '<a.*?>|</a>|/n |/ |\u200b|\xa0|<sub.*?>|</sub>|<img.*?>|<span.*?>|</span>|<strong>|</strong>'
    text_label = '//p/text()'
    form_label = '//tr/text()'
    bk360_character_experience=character_experience_extract(bk360_response,source,form_delete,text_delete,form_label,text_label)



    # #360社会任职信息提取
    form_delete = '\u2082|<a.*?>|</a>|\xa0|<sup.*?>|</sup>|<div.*?>|</div>|<td.*?>|<td>|\u200b|/ |/n|<sub.*?>|</sub>|<span.*?>|</span>|<strong>|</strong>'
    text_delete = '\u2082|<a.*?>|</a>|/n |/ |\u200b|\xa0|<sub.*?>|</sub>|<img.*?>|<span.*?>|</span>|<strong>|</strong>'
    form_label = '//tr/text()'
    text_label = '//p/text()'
    bk360_social_service=social_service_extract(bk360_response,source,form_delete,text_delete,form_label,text_label)


    #bk360主要成就信息提取
    form_delete = '\u2212|\u2217|\xf6|\ufb01|\xbe|\xee|\u30fb|<td.*?>|<div.*?>|</div>|<b>|</b>|<th>|<p>|</p>|<a.*?>|</a>|/n |/ |\u200b|\xa0|<sub.*?>|</sub>|<img.*?>|<span.*?>|</span>|<strong>|</strong>|进入技术百科.*?刘永才'
    text_delete = '\u2212|\u2217|\xf6|\ufb01|\xbe|\xee|\u30fb|<a.*?>|</a>|/n |/ |\u200b|\xa0|<sub.*?>|</sub>|<img.*?>|<span.*?>|</span>|<strong>|</strong>|进入技术百科.*?刘永才'
    form_label = '//tr/text()'
    text_label = '//div[@class="h2_content"]/p/text()|//div[@class="h3_content"]/p/text()'
    bk360_major_achievement = major_achievement_extract(bk360_response, source, form_delete, text_delete, form_label,text_label)

    #information_feedback(name,source,bk360_character_experience,bk360_social_service,bk360_major_achievement)
    # write_file(name,source,bk360_basic_information,bk360_character_experience,bk360_social_service,bk360_major_achievement)
    return(bk360_basic_information+bk360_character_experience+bk360_social_service+bk360_major_achievement)
