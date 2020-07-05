#-*- coding:utf-8 -*-
def information_feedback(name,source,character_experience,social_service,major_achievement):
    if character_experience == [] and social_service == [] and major_achievement == []:
        with open('3.txt', 'a+', encoding='utf-8') as f:
            f.write('%s：%s\n' % (name,source))
    if character_experience == [] and social_service == []:
        with open('人物经历与社会任职.txt', 'a+', encoding='utf-8') as f:
            f.write('%s：%s\n' % (name,source))
    if character_experience == []:
        with open('人物经历.txt', 'a+', encoding='utf-8') as f:
            f.write('%s：%s\n' % (name, source))
    if social_service == []:
        with open('社会任职.txt', 'a+', encoding='utf-8') as f:
            f.write('%s：%s\n' % (name, source))
    if major_achievement == []:
        with open('主要成就.txt', 'a+', encoding='utf-8') as f:
            f.write('%s：%s\n' % (name, source))