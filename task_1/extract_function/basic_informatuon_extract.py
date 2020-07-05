#-*- coding:utf-8 -*-
import re
from lxml import etree
def basic_information_extract(response,delete,option,value,div=''):
    basic_information = []
    response = re.sub(delete,'',response,flags=re.S|re.M)
    selector = etree.HTML(response)
    options = selector.xpath(option)
    if options != []:
    # 如果属性不为空，说明网页将基本信息做成字典形式了，按字典形式提取。
        values = selector.xpath(value)
        #删除options与values中多余的文本
        for i in range(len(options)):
            options[i] = re.sub(delete, '', options[i])
            options[i] = re.sub('\ |：|\xa0','',options[i])
        for i in range(len(values)):
            values[i] = re.sub(delete, '', values[i])
            values[i] = re.sub('\ |：|\xa0', '', values[i])
        basic_information = [options[i] + ':' +values[i] for i in range(len(options))]
        basic_information.insert(0,'基本信息')
        # print(basic_information)
        # basic_information = {o: v for o, v in zip(options, values)}
        # #输出以及返回
        # for key in basic_information:
        #     print(key,':',basic_information[key])
    else:
        if div == '':
            #如果div为空，说明div值没有填写正确
            print ('无法以字典形式提取，请以文本形式提取，请填写正确的div')
            return (basic_information)
        basic_information = selector.xpath(div)
        for i in range(len(basic_information)):
            basic_information[i] = re.sub('\xa9|\u2022', '', basic_information[i])
        basic_information.insert(0, '基本信息')
        # print(basic_information)


    return (basic_information)


