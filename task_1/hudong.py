#-*- coding:utf-8 -*-
from task_1.start_end.write_file import write_file
from task_1.start_end.crawl_data import crawl_data
from task_1.combine_start_end import combine_start_end
from task_1.extract_function.basic_informatuon_extract import basic_information_extract
from task_1.extract_function.character_experience_extract import character_experience_extract
from task_1.extract_function.social_service_extract import social_service_extract
from task_1.extract_function.major_achievement_extract import major_achievement_extract
from task_1.extract_function.information_feedback import information_feedback
def hudong_extract(name):
    source = '互动百科'
    #开始爬取数据
    hudong_response = crawl_data(name,source)

    #互动基本信息
    delete = '\xa0|\n|<a.*?>|</a>|<sup.*?>|</sup>|<img.*?>|</span>\s*<span>'
    option = '//div[contains(@id,"datamodule")]//strong/text()'
    value = '//div[contains(@id,"datamodule")]//span/text()'
    div = '//div[contains(@id,"unifyprompt")]/div[contains(@id,"anchor")]/p/text()'
    hudong_basic_information = basic_information_extract(hudong_response, delete, option, value,div)


    # #互动人物经历信息提取
    form_delete = '<a.*?>|</a>|\xa0|<sup.*?>|</sup>|<div.*?>|</div>|<td.*?>|<td>|\u2022|\t'
    text_delete = '<a.*?>|</a>|\xa0|\u2022|\t|<br />'
    form_label = '//tr/text()'
    text_label = '//p/text()|//div/text()'
    hudong_character_experience=character_experience_extract(hudong_response, source, form_delete, text_delete, form_label, text_label)


    # #互动社会任职提取
    form_delete = '\ufb01|\u2082|<a.*?>|</a>|\xa0|<sup.*?>|</sup>|<div.*?>|</div>|<td.*?>|<td>|\u2022|\t|进入技术百科.*?<h2刘永才'
    text_delete = '\ufb01|\u2082|<a.*?>|</a>|\xa0|\u2022|\t|进入技术百科.*?<h2刘永才'
    form_label = '//tr/text()'
    text_label = '//p/text()|//div/text()'
    hudong_social_service=social_service_extract(hudong_response, source, form_delete, text_delete, form_label, text_label)
    if hudong_social_service == []:
        #如果提取不出社会任职信息，有可能这些标题处于最后一个，需要用模式2来定位
        hudong_social_service = social_service_extract(hudong_response, source, form_delete, text_delete, form_label,text_label,2)
    #
    #
    #互动主要成就信息提取
    form_delete = '\u2212|\u2217|\xdf|\xdc|\xf6|\ufb01|\xa9|\xd8|\xbe|\xee|\u30fb|<td.*?>|<div.*?>|</div>|<b>|</b>|<a.*?>|</a>|\xa0|\u2022|\t|<br />|<sup.*?>|</sup>'
    text_delete = '\u2212|\u2217|\xdf|\xdc|\xf6|\ufb01|\xa9|\xd8|\xbe|\xee|\u30fb|<a.*?>|</a>|\xa0|\u2022|\t|<br />|<sup.*?>|</sup>'
    form_label = '//tr/text()'
    text_label = '//p/text()|//div/text()'
    hudong_major_achievement = major_achievement_extract(hudong_response, source, form_delete, text_delete, form_label,text_label)

    #information_feedback(name,source,hudong_character_experience,hudong_social_service,hudong_major_achievement)
    # write_file(name,source,hudong_basic_information,hudong_character_experience,hudong_social_service,hudong_major_achievement)
    return (hudong_basic_information+hudong_character_experience+hudong_social_service+hudong_major_achievement)
