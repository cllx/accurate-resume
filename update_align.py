from SStack import SStack
import cpca
from cpca import drawer
from DateFormatconvert2 import DateFormatHelper2
from cilin import CilinSimilarity
from queue import Queue,LifoQueue
from baidu_link_evidence import get_baike_page_citiao
import collections
import json
import re
import copy
import Levenshtein #字符串的编辑距离
import synonyms
import json
import os
import sys
import jieba
import xiaoqi

sys.setrecursionlimit(999)  # set the maximum depth as 5000
cs = CilinSimilarity()

#用于将地址信息进行对齐统一，接收参数为两个地址内容
def merge_local(fang_360, fang_baidu):
    location = []
    res_list = [] #返回值以列表形式，列表里的第一个数字表示返回值的状态
    #前面先处理为空的情况
    if fang_360!='' and fang_baidu=='':
        res_list = [0, fang_360]
    elif fang_baidu!='' and fang_360=='':
        res_list = [1, fang_baidu]
    elif fang_360=='' and fang_baidu=='':
        res_list = [4]
    else:
        if fang_360==fang_baidu:
            res_list = [2, fang_360]
        else:
            location = [fang_360,fang_baidu]
            df = cpca.transform(location) #实现地址信息格式的统一
            province = set()
            city = set()
            zone = set()
            address = set()
            for i in range(len(df['省'])):
                if df['省'][i]:
                    province.add(df['省'][i])
                if df['市'][i]:
                    city.add(df['市'][i])
                if df['区'][i]:
                    zone.add(df['区'][i])
                if df['地址'][i]:
                    address.add(df['地址'][i])
            if len(province)>1 or len(city)>1 or len(zone)>1 or len(address)>1: #表示地址描述不一致，需要消歧
                res_list = [3]
            else:
                last_location = '' #将对齐的内容挨个拼接起来作为返回值
                if len(province)==1:
                    last_location = last_location + list(province)[0]
                if len(city)==1:
                    last_location = last_location + list(city)[0]
                if len(zone)==1:
                    last_location = last_location + list(zone)[0]
                res_list = [2, last_location]
    return res_list

# 用于将日期信息进行对齐统一,接收参数为两个日期内容
def merge_date(fang_360, fang_baidu):
    res_list = []
    date = set()
    if fang_360!='' and fang_baidu=='': #第一个不为空
        formal_date = DateFormatHelper2.str2date(fang_360) #将日期格式进行统一
        res_list = [0, formal_date]
    elif fang_baidu!='' and fang_360=='': #第二个不为空
        formal_date = DateFormatHelper2.str2date(fang_baidu)
        res_list = [1, formal_date]
    elif fang_baidu=='' and fang_360=='': #两个都为空时
        res_list = [4]
    else: #都不为空时比较
        date.add(DateFormatHelper2.str2date(fang_baidu))
        date.add(DateFormatHelper2.str2date(fang_360))
        if len(date)==1: #两个相等时
            res_list = [2, list(date)[0]] #两个相等时
        else:
            year = set()
            month = set()
            day = set()
            for j in list(date):
                if j.find('-')>0:
                    res = j.split('-')
                    m = 1
                    for i in res:
                        if m==1:
                            year.add(i)
                            m += 1
                        elif m==2:
                            month.add(i)
                            m += 1
                        else:
                            day.add(i)
                            m += 1
                else:
                    year.add(j)
            if len(year)>1 or len(month)>1 or len(day)>1:
                res_list = [3] #表示日期不一致，无法对齐，需要消歧
            else:
                last_date = ''
                if len(year)==1:
                    last_date = last_date + list(year)[0]
                if len(month)==1:
                    last_date = last_date + '-' + list(month)[0]
                if len(day)==1:
                    last_date = last_date + '-' + list(day)[0]
                res_list = [2, last_date]
    return res_list #返回对齐合并后的日期

# 两个字符串的比较(看一个字符串是否是另一个字符串的子集)
def string_compile(str1, str2):
    str1 = re.split('_|\,|\/|\，|\、|\-|\ ' ,str1) #以这几个符号作为分割符切分两个字符串
    str2 = re.split('_|\,|\/|\，|\、|\-|\ ' ,str2)
    str1_len = len(str1)
    str2_len = len(str2)
    var_set = set(str1)
    return_str = ''
    for i in str2:
        var_set.add(i)
    if len(var_set) == str1_len:
        j = 0 
        for i in str1:
            if j+1 == str1_len:
                return_str = return_str+i
            else:
                return_str = return_str+i+'/'
            j += 1
        return return_str
    elif len(var_set) == str2_len:
        j = 0 
        for i in str2:
            if j+1 == str2_len:
                return_str = return_str+i
            else:
                return_str = return_str+i+'/'
            j += 1
        return return_str
    else:
        return 1
    
# 两个字符串的比较(看一个字符串是否是另一个字符串的子集)，使用结巴分词的方法
def jieba_compile(str1, str2):
    string1 = jieba.cut(str1,cut_all=False) #使用jieba的精确模式切分
    string2 = jieba.cut(str2,cut_all=False)
    new_string1 = []
    new_string2 = []
    special_char = ('、','\\','/',',','，','|','。',' ','_','-','&','#')
    for i in string1:
        if i not in special_char:
            new_string1.append(i)
    for i in string2:
        if i not in special_char:
            new_string2.append(i)
    str1_len = len(new_string1)
    str2_len = len(new_string2)
    var_set = set(new_string1)
    return_str = ''
    for i in new_string2:
        var_set.add(i)
    if len(var_set) == str1_len:
        j = 0 
        for i in new_string1:
            if j+1 == str1_len:
                return_str = return_str+i
            else:
                return_str = return_str+i+'/'
            j += 1
        return return_str
    elif len(var_set) == str2_len:
        j = 0 
        for i in new_string2:
            if j+1 == str2_len:
                return_str = return_str+i
            else:
                return_str = return_str+i+'/'
            j += 1
        return return_str
    else:
        return 1
  
'''
文件都是列表时的对齐，接收参数是属性内容列表attribute_value_list，对应的百科文件的名字，以及前一轮消歧标记的数
整体思路与内容是字典时的比较一样，也是先比较内容列表里的前两个值，比较的结果放入列表后面
当列表长度为1的时候就返回，否则继续比较
'''
def compile_list(attribute_value_list, baike_name, disambiguate_flag):
    new_attribute_list = [] #用于保存列表里不为空的内容，只比较不为空的内容
    new_baike_name = [] #用于保存不为空的内容的信息来源(百科文件名)
    # 循环的目的是为了将属性内容为空的值去掉，只比较不为空的内容
    j = 0
    for i in attribute_value_list:
        if i!='' and len(i)>0:
            new_attribute_list.append(i)
            if j < len(baike_name): #因为每进行列表里两个内容的比较后，相应的内容和百科名会从原列表中删除
                new_baike_name.append(baike_name[j])
            else:
                pass
        j += 1
    temp_list = [] #一个临时列表变量，用于存储每一轮比较的结果(无论是消歧、对齐还是都保留的结果)
    if len(new_attribute_list)>1: #当列表长度大于1的时候，继续比较
        list_baike1 = new_attribute_list[0]
        list_baike2 = new_attribute_list[1]
        keys = list_baike1[0].keys() #取出值列表中的所有键名
        #下面这两个循环先把时间格式进行统一了
        for i in list_baike1:
            for key in keys:
                if key == '起始时间' or key == '终止时间' or key == '结束时间' or key == '时间':
                    if i[key] != '':
                        i[key] = DateFormatHelper2.str2date(i[key])
        for i in list_baike2:
            for key in keys:
                if key == '起始时间' or key == '终止时间' or key == '结束时间' or key == '时间':
                    if i[key] != '':
                        i[key] = DateFormatHelper2.str2date(i[key])
        second_align_list = [] #这一个专门记录比较过程中第二个文件进行了消歧和对齐的部分
        #遍历两个文件内容中每个键名下的值并比较，当大于等于2个键不相同时则不进行消歧标记，
        #只有1个键值不同，其他键值都相同时则进行消歧标记
        #如果所有键值都相同，则说明是对齐了的，进行合并
        for first_file_key_value in list_baike1:
            mark_first_flag = 0 #用于标记第一个文件的当前行内容是否进行了对齐或消歧操作，如果没有进行就保留下来
            first_temp_dict = copy.deepcopy(first_file_key_value) #用于将第一个文件当前行的字典保存下来
            for second_file_key_value in list_baike2:
                second_temp_dict = copy.deepcopy(second_file_key_value) #用于将第二个文件当前行的字典保存下来
                align_disambiguate_flag = 0 #比较过程中用于记录键值不相同的个数，辅助判断是否需要消歧
                for key in keys:
                    if key != '消歧标记' and key != '来源': #消歧标记和来源的信息不进行比较
                        if key == '起始时间' or key == '终止时间' or key == '结束时间' or key == '时间':
                            if first_file_key_value[key]!='' and  second_file_key_value[key]!='':
                                res = merge_date(first_file_key_value[key], second_file_key_value[key])
                                if res[0] == 3:
                                    align_disambiguate_flag += 1
                            elif first_file_key_value[key]!='' and  second_file_key_value[key]=='':
                                align_disambiguate_flag += 1
                            elif first_file_key_value[key]=='' and  second_file_key_value[key]!='':
                                align_disambiguate_flag += 1
                            else:
                                pass
                        elif key == '地点':
                            if first_file_key_value[key]!='' and  second_file_key_value[key]!='':
                                res = merge_local(first_file_key_value[key], second_file_key_value[key])
                                if res[0] == 3:
                                    align_disambiguate_flag += 1
                            elif first_file_key_value[key]!='' and  second_file_key_value[key]=='':
                                align_disambiguate_flag += 1
                            elif first_file_key_value[key]=='' and  second_file_key_value[key]!='':
                                align_disambiguate_flag += 1
                            else:
                                pass
                        else:
                            string_include_res = string_compile(first_file_key_value[key], second_file_key_value[key])
                            cilin_res = cs.similarity(first_file_key_value[key], second_file_key_value[key])
                            content_distance = Levenshtein.distance(first_file_key_value[key],second_file_key_value[key])
                            '''
                            不能用jieba分词来判断两个字符串是否重合，同找到一个字符串在另一个字符串中是否存在
                            一样的问题，可能会把本来需要消歧的内容也对齐了，比如委员和技术委员会委员等
                            '''
                            #jieba_include_res = jieba_compile(first_file_key_value[key], second_file_key_value[key])
                            if (first_file_key_value[key] != second_file_key_value[key]) and string_include_res==1 and cilin_res!=1:
                                res = get_baike_evaluate(key, first_file_key_value, second_file_key_value)
                                if res == 0:
                                    pass
                                else:
                                    align_disambiguate_flag += 1
                if align_disambiguate_flag > 1: #表示至少有两个键值不一样，不进行对齐与消歧
                    pass
                elif align_disambiguate_flag == 1: #表示只有一个键值不一样，进行消歧标记
                    #这一段专门处理消歧标记的问题
                    if ('消歧标记' in first_temp_dict) and ('消歧标记' not in second_temp_dict):
                        second_temp_dict['消歧标记'] = first_temp_dict['消歧标记']
                    elif ('消歧标记' not in first_temp_dict) and ('消歧标记' in second_temp_dict):
                        first_temp_dict['消歧标记'] = second_temp_dict['消歧标记']
                    elif ('消歧标记' in first_temp_dict) and ('消歧标记' in second_temp_dict):
                        first_temp_dict['消歧标记'] = second_temp_dict['消歧标记']
                    else:
                        first_temp_dict['消歧标记'] = disambiguate_flag
                        second_temp_dict['消歧标记'] = disambiguate_flag
                        disambiguate_flag += 1
                    #这一段专门处理来源的问题
                    if ('来源' not in first_temp_dict) and ('来源' not in second_temp_dict):
                        first_temp_dict['来源'] = new_baike_name[0]
                        second_temp_dict['来源'] = new_baike_name[1]
                    elif ('来源' in first_temp_dict) and ('来源' not in second_temp_dict):
                        second_temp_dict['来源'] = new_baike_name[0]
                    elif ('来源' not in first_temp_dict) and ('来源' in second_temp_dict):
                        first_temp_dict['来源'] = new_baike_name[0]
                    else:
                        pass
                    mark_first_flag = 1
                    second_align_list.append(second_file_key_value)
                    temp_list.append(first_temp_dict)
                    temp_list.append(second_temp_dict)
                    break
                else: #表示所有键值都一样，进行对齐合并
                    if ('消歧标记' in first_temp_dict) and ('消歧标记' not in second_temp_dict):
                        pass
                    elif ('消歧标记' not in first_temp_dict) and ('消歧标记' in second_temp_dict):
                        first_temp_dict['消歧标记'] = second_temp_dict['消歧标记']
                    elif ('消歧标记' in first_temp_dict) and ('消歧标记' in second_temp_dict):
                        first_temp_dict['消歧标记'] = second_temp_dict['消歧标记']
                    else:
                        pass
                    if ('来源' not in first_temp_dict) and ('来源' not in second_temp_dict):
                        first_temp_dict['来源'] = new_baike_name[0]+','+new_baike_name[1]
                    elif ('来源' in first_temp_dict) and ('来源' not in second_temp_dict):
                        first_temp_dict['来源'] = first_temp_dict['来源']+','+new_baike_name[0]
                    elif ('来源' not in first_temp_dict) and ('来源' in second_temp_dict):
                        first_temp_dict['来源'] = second_temp_dict['来源']+','+new_baike_name[0]
                    else:
                        first_temp_dict['来源'] = first_temp_dict['来源']+','+second_temp_dict['来源']
                    mark_first_flag = 1
                    second_align_list.append(second_file_key_value)
                    temp_list.append(first_temp_dict)
                    break
            if mark_first_flag == 0:
                if ('来源' not in first_temp_dict):
                    first_temp_dict['来源'] = new_baike_name[0]
                temp_list.append(first_temp_dict)
        #用于在第二个文件属性中找到还未处理的部分
        if ('消歧标记' in keys) and ('来源' in keys):
            length = len(keys) - 2
        elif ('消歧标记' not in keys) and ('来源' in keys):
            length = len(keys) - 1
        else:
            length = len(keys)
        for second_file_key_value in list_baike2:
            flag = 0 #用于记录是否有在已对齐或消歧的列表里找到相同的
            for second_file_pre_process in second_align_list:
                for key in keys:
                    if key != '消歧标记' and key != '来源':
                        if second_file_key_value[key] != second_file_pre_process[key]:
                            flag = 0
                            break
                        else:
                            flag += 1
                if flag == length-1:
                    break
                    flag = 0
            if flag == 0:
                if ('来源' not in second_file_key_value):
                    second_file_key_value['来源'] = new_baike_name[1]
                temp_list.append(second_file_key_value)
        duplicate_removal_temp_res = duplicate_removal(temp_list) #得到去重后的结果
        duplicate_removal_res = removal_signal_xiaoqi(duplicate_removal_temp_res) #将结果中只有一个标记的标记信息去掉
        new_attribute_list.append(duplicate_removal_res) #将对齐、消歧处理后且去重后的结果添加到原属性列表后
        #每处理一轮就把前两个删掉
        del new_attribute_list[0]
        del new_attribute_list[0]
        if len(new_baike_name) > 1: #如果百科名列表大于等于两个就删除前两个
            del new_baike_name[0]
            del new_baike_name[0]
        elif len(new_baike_name) == 1: #如果百科名列表只有一个就删除前两个
            del new_baike_name[0]
        else:
            pass
        return compile_list(new_attribute_list, new_baike_name, disambiguate_flag)
    elif len(new_attribute_list) == 0:
        return 0
    else:
        if j != 1: #表示最开始的文件属性列表中，就只有一个不为空，其他都为空的情况
            for i in new_attribute_list[0]:
                i['来源'] = new_baike_name[0]
            return new_attribute_list[0]
        return new_attribute_list[0]

'''
专门用于处理查找百科外链的部分，接收参数为当前要查找的key，要查找比较的两个内容
主要查找除职称、任免职位_职称、职位_职称、授予奖项名称、教育理念等以外的内容
而针对以上这几个内容是默认未对齐的
而针对其他键的内容进行百科搜索对齐时也主要是考虑起始时间或时间点是相同年份的
'''
def get_baike_evaluate(key, first_file_key_value, second_file_key_value):
    if (first_file_key_value[key]!='' and second_file_key_value[key]=='') or (first_file_key_value[key]=='' and second_file_key_value[key]!=''):
        return 1 #一个为空一个不为空的情况也表示未对齐
    flag = 0 #用于标记时间是否一样
    if key!='职称' and key!='任免职位_职称' and key!='职位_职称' and key!='荣誉' and key!='教育理念':
        if '起始时间' in first_file_key_value.keys():
            if first_file_key_value['起始时间'] == second_file_key_value['起始时间']:
                flag = 1
        if '时间' in first_file_key_value.keys():
            if first_file_key_value['时间'] == second_file_key_value['时间']:
                flag = 1
        if flag == 1:
            res = get_baike_page_citiao.get_baike_page_citiao(first_file_key_value[key], second_file_key_value[key])
            if res[0]==0 and res[1]==0: #表示都能找到对应的百科词条
                if res[2]==res[3]:
                    return 0 #返回0表示能对齐
                else:
                    return 1 #返回1表示不能对齐
            else:
                return 1
        else:
            return 1
    else:
        return 1
    
#用于去掉temp_list中重复的数据，优先保留"消歧标记"数最多的数据，如果都有"消歧标记"，则保留"来源更多"的数据
def duplicate_removal(temp_list):
    keys = temp_list[0].keys()
    duplicate_removal_list = [] #用于存储去重后的元素
    for i in range(0,len(temp_list)):
        #把当前的元素赋给一个最多"来源"数的变量，后续用这个变量来比较,
        #并且碰到来源数更多的重复元素时，将max_source_num替换为更多"来源"的那个重复元素
        #比较过的重复的元素都打上一个"删除标记"，以便在后续循环时不再参与比较
        if '删除标记' in temp_list[i]: #碰到已经比较过的重复的元素，就跳过本次循环
            continue
        max_source_num = copy.deepcopy(temp_list[i])
        for j in range(i+1, len(temp_list)):
            if '删除标记' in temp_list[j]: #碰到已经比较过的重复的元素，就跳过本次循环
                continue
            flag = 0
            for key in keys:
                if key!='消歧标记' and key!='来源' and key!='删除标记':
                    if key == '起始时间' or key == '终止时间' or key == '结束时间' or key == '时间':
                        res = merge_date(max_source_num[key], temp_list[j][key])
                        if res[0] != 2 and res[0] != 4:
                            flag += 1
                    elif key=='职称' or key=='任免职位_职称' or key=='颁奖单位' or key=='组织单位_活动单位名称' or key=='所在单位':
                        res = string_compile(max_source_num[key], temp_list[j][key])
                        if res == 1:
                            flag += 1
                    elif key=='项目':
                        exist_or_duplicate1 = max_source_num[key].find(temp_list[j][key])
                        exist_or_duplicate2 = temp_list[j][key].find(max_source_num[key])
                        if exist_or_duplicate1<0 and exist_or_duplicate2<0:
                            flag += 1
                    else:
                        #if max_source_num[key] != temp_list[j][key]:
                        if Levenshtein.distance(max_source_num[key],temp_list[j][key]) > 4:
                            flag += 1
            if flag == 0: #表示找到了一个重复的，优先保留有"消歧标记"的，其次保留"来源"更多的
                if ('消歧标记' in temp_list[j]) and ('消歧标记' not in max_source_num):
                    max_source_num = copy.deepcopy(temp_list[j])
                elif ('消歧标记' not in temp_list[j]) and ('消歧标记' in max_source_num):
                    pass
                else: #这里表示要么都没"消歧标记"，要么都有"消歧标记"，两种情况下都是优先保留'来源'更多的
                    if compute_source_num(temp_list[j]['来源']) > compute_source_num(max_source_num['来源']):
                        max_source_num = copy.deepcopy(temp_list[j])
                    # 来源一样多的时候,保留内容更长的那一个
                    elif compute_source_num(temp_list[j]['来源'])==compute_source_num(max_source_num['来源']):
                        for tmp_key in temp_list[j].keys():
                            if tmp_key not in ['时间', '起始时间', '终止时间', '来源', '消歧标记', '删除标记']:
                                if len(temp_list[j][tmp_key]) > len(max_source_num[tmp_key]):
                                    max_source_num = copy.deepcopy(temp_list[j])
                    else:
                        pass
                temp_list[j]['删除标记'] = 1
        duplicate_removal_list.append(max_source_num)
    return duplicate_removal_list

#去掉结果中某个标记只有一个的时候该内容的标记部分
def removal_signal_xiaoqi(temp_list):
    keys = temp_list[0].keys()
    for i in range(0,len(temp_list)):
        if '删除标记' in temp_list[i]:
            continue
        flag = 0 #用于标记是否与它有相同"消歧标记"内容的情况
        if '消歧标记' in temp_list[i]:
            for j in range(i+1, len(temp_list)):
                if '消歧标记' in temp_list[j]:
                    if temp_list[i]['消歧标记'] == temp_list[j]['消歧标记']:
                        temp_list[j]['删除标记'] = 1
                        flag = 1
            if flag == 0:
                del temp_list[i]['消歧标记'] #如果没有发现有与其相同的"消歧标记"值，就删除其的"消歧标志"的键值对
    #将前面辅助用到的删除标记去掉
    for i in temp_list:
        if '删除标记' in i:
            del i['删除标记']
    return temp_list
    
# 按,分割来源字符串，并计算得到的最终长度,接收参数为来源字符串
def compute_source_num(source):
    res = source.split(',')
    return len(res)
    
# 将结果写入到新json文件中，接收参数为当前属性名word和要存入的结果res
def list_to_newjson(word, res):
    if word=='本科' or word=='硕士研究生' or word=='博士研究生':
        align_json['人物履历']['教育经历'][word]=res
    elif word=='博士后' or word=='任职' or word=='任免_辞职':
        align_json['人物履历']['工作经历'][word]=res
    elif word=='科研方向' or word=='研究领域' or word=='主要荣誉' or word=='学术论著类' or word=='散文类' or word=='承担项目类' or word=='研究成果类' or word=='发明专利类' or word=='人才培养类':
        align_json['成就'][word]=res
    else:
        align_json[word]=res

# 只取日期前面的年份
def get_year(date):
    if date!='':
        date = date.strip()
        year = date[:4]
        year = year + '年'
        return year
    return date

'''
维护一个键的队列，输入参数为当前的属性名key和当前的队列的状态key_queue
当遇到key为下面的值的时候，不仅弹出当前的key，还弹出其前一个即父类的key
'''
def preserve_key_queue(key, key_queue):
    if key=='人才培养类' or key=='博士研究生':
        delete = key_queue.get()
    elif key=='任免_辞职':
        delete = key_queue.get()
        delete = key_queue.get()
    else:
        pass

'''
把字典型数据里子属性为时间、地点和其他类型的值进行比较处理，通过参数genre来判断具体是比较哪一类型的值
这里主要的思路是每次比较属性内容列表里前两个的值，比较的结果放入到列表末尾(无论是对齐的还是需要消歧的)
当列表长度为1的时候，即表明比较结束，将比较结果返回
'''
def dict_deal(content_list, index, baike_name, genre):
    null_flag = 0
    for if_null in content_list:
        if if_null != '':
            null_flag = 1
            break
    if null_flag == 0:
        string = ''
        return string
    if len(content_list)>1: #当content_list列表里不止一个元素时，继续比较，直到只剩一个元素才返回
        tmp_dict1 = {} #中间变量，用于对其中一个文件的内容在对齐与消歧时做标记
        tmp_dict2 = {} #中间变量，用于对另一个文件的内容在对齐与消歧时做标记
        tmp_list = [] #临时变量，用于在消歧时记录两个文件内容的状态
        if type(content_list[0]).__name__=='str' and type(content_list[1]).__name__=='str':
            if genre == "其他":
                res = compare_other(content_list[0], content_list[1])
            elif genre == "地点":
                res = merge_local(content_list[0], content_list[1])
            else:
                res = merge_date(content_list[0], content_list[1])
            if res[0]==2: #标识都不为空且是对齐了的
                tmp_dict1[index] = res[1]
                tmp_dict1['来源'] = baike_name[0]+','+baike_name[1]
                content_list.append(tmp_dict1)
            elif res[0]==4: #表示两个都为空值
                pass
            elif res[0]==0: #表示content_list[0]不为空，content_list[1]为空
                tmp_dict1[index] = res[1]
                tmp_dict1['来源'] = baike_name[0]
                content_list.append(tmp_dict1)
            elif res[0]==1: #表示content_list[0]为空，content_list[1]不为空
                tmp_dict1[index] = res[1]
                tmp_dict1['来源'] = baike_name[1]
                content_list.append(tmp_dict1)
            else: #标识两个都不为空，且未对齐
                tmp_dict1[index] = content_list[0]
                tmp_dict1['消歧标记'] = 1
                tmp_dict1['来源'] = baike_name[0]
                tmp_dict2[index] = content_list[1]
                tmp_dict2['消歧标记'] = 1
                tmp_dict2['来源'] = baike_name[1]
                tmp_list = [tmp_dict1, tmp_dict2]
                content_list.append(tmp_list)
            del baike_name[0] #注意删除的时候的问题，连续删除两个的话，删除了第1个过后列表长度会减1
            del baike_name[0]
            del content_list[0]
            del content_list[0]
        elif type(content_list[0]).__name__=='str' and type(content_list[1]).__name__=='dict':
            if genre == "其他":
                res = compare_other(content_list[0], content_list[1][index])
            elif genre == "地点":
                res = merge_local(content_list[0], content_list[1][index])
            else:
                res = merge_date(content_list[0], content_list[1][index])
            if res[0]==2: #标识都不为空且是对齐了的
                tmp_dict1[index] = res[1]
                tmp_dict1['来源'] = content_list[1]['来源']+','+baike_name[0]
                content_list.append(tmp_dict1)
            elif res[0]==4: #表示两个都为空值
                pass
            elif res[0]==0: #表示content_list[0]不为空，content_list[1]为空
                pass
            elif res[0]==1: #表示content_list[0]为空，content_list[1]不为空
                content_list.append(content_list[1])
            else: #标识两个都不为空，且未对齐
                tmp_dict1[index] = content_list[0]
                tmp_dict1['消歧标记'] = 1
                tmp_dict1['来源'] = baike_name[0]
                content_list[1]['消歧标记'] = 1
                tmp_list = [content_list[1], tmp_dict1]
                content_list.append(tmp_list)
            del baike_name[0]
            del content_list[0]
            del content_list[0]
        elif type(content_list[0]).__name__=='dict' and type(content_list[1]).__name__=='dict':
            if genre == "其他":
                res = compare_other(content_list[0][index], content_list[1][index])
            elif genre == "地点":
                res = merge_local(content_list[0][index], content_list[1][index])
            else:
                res = merge_date(content_list[0][index], content_list[1][index])
            if res[0]==2: #标识都不为空且是对齐了的
                tmp_dict1[index] = res[1]
                tmp_dict1['来源'] = content_list[1]['来源']+','+content_list[0]['来源']
                content_list.append(tmp_dict1)
            elif res[0]==3:
                content_list[0]['消歧标记'] = 1
                content_list[1]['消歧标记'] = 1
                tmp_list = [content_list[0], content_list[1]]
                content_list.append(tmp_list)
            else:
                pass
            del content_list[0]
            del content_list[0]
        elif type(content_list[0]).__name__=='str' and type(content_list[1]).__name__=='list':
            flag = 0
            for i in content_list[1]:
                if genre == "其他":
                    res = compare_other(content_list[0], i[index])
                elif genre == "地点":
                    res = merge_local(content_list[0], i[index])
                else:
                    res = merge_date(content_list[0], i[index])
                if res[0]==2: #标识都不为空且是对齐了的
                    i[index] = res[1]
                    i['来源'] = i['来源']+','+baike_name[0]
                    content_list.append(content_list[1])
                    flag = 1
                    break
                elif res[0]==4: #表示两个都为空值
                    pass
                elif res[0]==0: #表示content_list[0]不为空，content_list[1]为空
                    pass
                elif res[0]==1: #表示content_list[0]为空，content_list[1]不为空
                    content_list.append(content_list[1])
                    flag = 1
                    break
                else: #标识两个都不为空，且未对齐
                    pass
            if flag==1:
                del baike_name[0]
                del content_list[0]
                del content_list[0]
            else:
                tmp_dict1[index] = content_list[0]
                tmp_dict1['消歧标记'] = 1
                tmp_dict1['来源'] = baike_name[0]
                tmp_list = [tmp_dict1]
                for i in content_list[1]:
                    tmp_list.append(i)
                content_list.append(tmp_list)
                del baike_name[0]
                del content_list[0]
                del content_list[0]
        elif type(content_list[0]).__name__=='dict' and type(content_list[1]).__name__=='list':
            flag = 0
            for i in content_list[1]:
                if genre == "其他":
                    res = compare_other(content_list[0][index], i[index])
                elif genre == "地点":
                    res = merge_local(content_list[0][index], i[index])
                else:
                    res = merge_date(content_list[0][index], i[index])
                if res[0]==2:
                    i[index] = res[1]
                    i['来源'] = i['来源']+','+content_list[0]['来源']
                    content_list.append(content_list[1])
                    flag = 1
                    break
                else:
                    pass
            if flag==1:
                del content_list[0]
                del content_list[0]
            else:
                content_list[0]['消歧标记'] = 1
                tmp_list = [content_list[0]]
                for i in content_list[1]:
                    tmp_list.append(i)
                content_list.append(tmp_list)
                del content_list[0]
                del content_list[0]
        elif type(content_list[0]).__name__=='list' and type(content_list[1]).__name__=='dict':
            flag = 0
            for i in content_list[0]:
                if genre == "其他":
                    res = compare_other(content_list[1][index], i[index])
                elif genre == "地点":
                    res = merge_local(content_list[1][index], i[index])
                else:
                    res = merge_date(content_list[1][index], i[index])
                if res[0]==2:
                    i[index] = res[1]
                    i['来源'] = i['来源']+','+content_list[1]['来源']
                    content_list.append(content_list[0])
                    flag = 1
                    break
                else:
                    pass
            if flag==1:
                del content_list[0]
                del content_list[0]
            else:
                content_list[1]['消歧标记'] = 1
                tmp_list = [content_list[1]]
                for i in content_list[0]:
                    tmp_list.append(i)
                content_list.append(tmp_list)
                del content_list[0]
                del content_list[0]
        elif type(content_list[0]).__name__=='list' and type(content_list[1]).__name__=='list':
            flag_list = []
            for i in content_list[0]:
                flag = 0
                for j in content_list[1]:
                    if genre == "其他":
                        res = compare_other(i[index], j[index])
                    elif genre == "地点":
                        res = merge_local(i[index], j[index])
                    else:
                        res = merge_date(i[index], j[index])
                    if res[0]==2:
                        i[index] = res[1]
                        i['来源'] = i['来源']+','+j['来源']
                        tmp_list.append(i)
                        flag = 1
                        flag_list.append(j)
                        break
                    else:
                        pass
                if flag==0:
                    tmp_list.append(i)
            for i in content_list[1]:
                flag = 0
                for j in flag_list:
                    if i[index]!=j[index]:
                        pass
                    else:
                        flag = 1
                        break
                if flag == 0:
                    tmp_list.append(i)
            content_list.append(tmp_list)
            del content_list[0]
            del content_list[0]
        else:
            pass
        return compare(content_list, index, baike_name)
    else:
        if len(baike_name) == 0:
            return content_list[0]
        else:
            tmp_dict = {}
            tmp_dict[index] = content_list[0]
            tmp_dict['来源'] = baike_name[0]
            content_list.append(tmp_dict)
            del content_list[0]
            return content_list[0]

'''
比较字典型数据里的子属性的值,输入参数是不同百科该子属性值的列表和对应的属性名
这里主要的思路是每次比较属性内容列表里前两个的值，比较的结果放入到列表末尾(无论是对齐的还是需要消歧的)
当列表长度为1的时候，即表明比较结束，将比较结果返回
'''
def compare(content_list, index, baike_name):
    if index=='起始时间' or index=='终止时间' or index=='结束时间' or index=='出生日期' or index=='时间':
        res = dict_deal(content_list, index, baike_name, '时间')
    elif index=='出生地' or index=='原籍' or index=='地点':
        res = dict_deal(content_list, index, baike_name, '地点')
    else: #除开时间、地址的其他情况对齐
        res = dict_deal(content_list, index, baike_name, '其他')
    return res
    
# 根据库比较除时间、地点外其他值是否对齐，接收的参数为两个文件属性的值，以列表形式返回，一个是内容一个是标识
def compare_other(content1, content2):
    res_list = [] #以列表形式返回，一个是内容一个是标识
    if content1!='' and content2=='':
        res_list = [0, content1] #标识第一个不为空，第二个为空
    elif content1=='' and content2!='': 
        res_list = [1, content2] #标识第一个为空，第二个不为空
    elif content1!='' and content2!='':
        if content1==content2:
            res_list = [2, content1]
        else:
            res = cs.similarity(content1, content2)
            if res==1:
                res_list = [2, content1] #标识两个都不为空且是对齐的
            else:
                res_list = [3] #标识两个都不为空，但未对齐
    else:
        res_list = [4] #标识两个都为空
    return res_list
 
'''
# 对非列表且是字典形式的内容进行对齐(这里主要关注基本信息这个模块)
# 接收参数为属性值列表和百科文件名
# 按照时间、地点和其他信息处理
'''
def align_dict(attribute_value_list, baike_name):
    new_attribute_list = [] #用于保存列表里不为空的内容，只比较不为空的内容
    new_baike_name = [] #用于保存不为空的内容的信息来源(百科文件名)
    #循环的目的是为了将属性内容为空的值去掉，只比较不为空的内容
    j = 0
    for i in attribute_value_list:
        if i != '':
            new_attribute_list.append(i)
            new_baike_name.append(baike_name[j])
        j += 1
    keys = list(new_attribute_list[0].keys()) #得到该属性下的所有键的名字，并放到一个list里
    new_dict = {} #用于存放对齐与未对齐(需消歧)后的内容
    for index in keys:
        value = []
        for i in new_attribute_list:
            value.append(i[index])
        var_baike_name = copy.deepcopy(new_baike_name)
        res = compare(value, index, var_baike_name)
        new_dict[index] = res
    return new_dict
                                                        
# 对非列表非字典形式的内容对齐(也包括都是列表，但列表里面都是字符串，不是字典的情况)
def string_align(word, content_list):
    new_list = []
    list_to_set = set() #把list里的内容放到集合中，实现自动去重
    #根据是否是字符串、是否为空、是否是列表、列表是否为空几个情况来判断执行
    for i in content_list:
        if i=='':
            continue
        elif type(i).__name__ == 'list' and len(i)>0:
            for j in i:
                if j!='':
                    list_to_set.add(j)
        elif type(i).__name__ != 'list':
            list_to_set.add(i)
        else:
            pass
    new_list = list(list_to_set)
    print(new_list)
    # 去除相似度比较高的部分(有些类似于冒泡排序的处理方式)
    for i in range(0, len(new_list)):
        #temp = i
        for j in range(i+1, len(new_list)):
            if synonyms.compare(new_list[i], new_list[j])>0.5 or Levenshtein.ratio(new_list[i], new_list[j])>0.8:
                if len(new_list[i]) > len(new_list[j]):
                    new_list[i] = new_list[j]
                else:
                    new_list[j] = new_list[i]
    new_list = list(set(new_list))
    return new_list

'''
由于任务二的抽取部分对本来应该是单真值的教育经历造成出现多个值的情况，无法对来自同一个百科的多个教育经历的值进行 
真伪验证(比如来自百度百科的本科教育会出现多个不同的学校)，所以只能事先对同一个百科的多个值的同一个教育经历打上消
歧标志
'''
def education_add_xiaoqibiaoshi(attribute_value_list):
    new_attribute_value_list = []
    for baike_education_list in attribute_value_list:
        temp = []
        if len(baike_education_list) > 0:
            for i in baike_education_list:
                i['消歧标记'] = 0
                temp.append(i)
            new_attribute_value_list.append(temp)
        else:
            new_attribute_value_list.append(baike_education_list)
    return new_attribute_value_list

'''本函数用户判断某个属性对应的值的类型，并根据类型调用相应的函数处理，
   接受参数为维护的栈和队列，以及各百科文件的来源名
   当属性队列为空的时候，返回0
'''
def other_align(st, key_queue, baike_name):
    if not st.is_empty():
        content = set()
        word = st.pop() #弹出当前栈里面顶上的内容
        key_queue.put(word) #键值队列，用于保存前面已出现的键值(目的是方便后面迭代时能准确找到进行到什么地方了)
        index = 0 #index变量，用于在json_file(百科的json文件列表)里找到对应的百科文件
        attribute_value_list = [] #局部列表变量，用于存储不同百科文件当前属性下的值
        for i in baike_name:
            p = json_file[index] #将当前遍历获得的百科文件存入到变量P里面
            key_str = 'p'
            for j in key_queue.queue: #通过维护的键的队列取到对应的键值
                key_str = key_str+'[\''+j+'\']'
            print(key_str)
            attribute_value_list.append(eval(key_str))
            index += 1
        flag = 0 #标记这几个百科json文件的当前属性值是否为空
        '''
        这里之所以遍历查看的原因是可能五个文件中有些该属性的值为空，但其他文件却为list或dict，
        如果先遍历到为空的文件，也先不管，还是继续遍历，直到找到不为空的，执行相应的操作,
        但一旦遍历到了不为空的，就可以break退出循环，以免重复进行操作
        '''
        for i in attribute_value_list:
            new_baike_name = copy.deepcopy(baike_name)
            if type(i).__name__ == 'list': #处理百科json文件中该属性下的值如果是列表时的情况，则取出列表里的每一个字典
                flag = 1
                if word=='人物影响' or word=='研究领域' or word=='人才培养类' or word=='发明专利类' or word=='科研方向' or word=='散文类': #这六个属性的值没有子属性了，其值直接就是字符串形式，所以单独处理
                    res = string_align(word, attribute_value_list)
                    list_to_newjson(word, res)
                    key = key_queue.get()
                    preserve_key_queue(key, key_queue)
                    other_align(st, key_queue, new_baike_name)
                else: #其他情况的属性值里还有子属性，此时如果是列表的话也是单独处理
                    if len(i)!=0 and type(i[0]).__name__ != 'dict': #这里之所以这样判断是因为抽取结果中可能存在列表中其他情况也是全字符串的情况(没有抽出时间)
                        res = string_align(word, attribute_value_list)
                        list_to_newjson(word, res)
                        key = key_queue.get()
                        preserve_key_queue(key, key_queue)
                        other_align(st, key_queue, new_baike_name)
                    else:
                        # 对这几个本来是单真值却出现多个值的情况事先先打上消歧标志
                        if word=='本科' or word=='硕士研究生' or word=='博士研究生':
                            attribute_value_list = education_add_xiaoqibiaoshi(attribute_value_list)
                        res = compile_list(attribute_value_list, new_baike_name, 0) #返回的是一个列表，列表里面是多个字典
                        if res==0:
                            res=''
                        list_to_newjson(word,res)
                        key = key_queue.get()
                        preserve_key_queue(key, key_queue) #得到动态维护的键的队列
                        other_align(st, key_queue, new_baike_name)
                break
            elif type(i).__name__ == 'dict': #处理百科json文件中该属性下的值如果是字典时的情况，这里主要是针对单属性值
                flag = 1
                if word=='基本信息':
                    res = align_dict(attribute_value_list, new_baike_name)
                    list_to_newjson(word,res)
                    key = key_queue.get()
                    preserve_key_queue(key, key_queue)
                    other_align(st, key_queue, new_baike_name)
                else: #当不是单属性值时，说明其还不是最外层的属性(也即为父属性)，则将其压入栈中后续出栈时再处理
                    dict_key1 = list(i.keys()) #将字典里的键都放入栈中，稍后依次取出进行对齐
                    dict_key1.reverse()
                    for i in dict_key1:
                        st.push(i)
                    other_align(st, key_queue, new_baike_name)
                break
            else:
                pass
        if flag==0: #表示这几个文件的当前属性都为空
            res = ''
            list_to_newjson(word, res)
            key = key_queue.get()
            preserve_key_queue(key, key_queue)
            other_align(st, key_queue, new_baike_name)
    else:
        return 0

# 对齐处理的入口函数，接收参数为最外层的属性名列表和对应的百科json文件名列表
def process_entrace(key_list, baike_name, yuanshi_name):
    tree=lambda:collections.defaultdict(tree)
    global align_json #全局变量，用于存储对齐和未对齐(做标记)的结果
    align_json=tree()
    st = SStack() #用栈存放每一轮的属性
    lq = LifoQueue(maxsize=0) #用后进先出队列用于存放文件操作过程中的中间键值(用于新建新的对齐json)
    key_list.reverse() #属性名列表反向，为了使最后按照正向的方式写入
    for i in key_list:
        st.push(i) #将最开始外层的属性名压入栈中
    res = other_align(st, lq, baike_name) #调用对齐的控制函数
    align_json['院士名'] = yuanshi_name
    path = '/home/chenxl/data_mining_resume/static/align_json/'+yuanshi_name+'.json'
    align_json = json.dumps(align_json,ensure_ascii=False,indent=4)
    with open(path, 'w') as f:
        f.write(align_json) #设置不转换成ascii  json字符串首缩进
    return align_json

def main(extract_result):
    global json_file #全局列表变量，用于存放不同百科json文件的内容
    json_file = []
    baike_name = [] #局部变量，用于存放json百科文件的名字，对应数据来源
    for i in extract_result:
        json_file.append(i)
        baike_name.append(i['百科名'])
    key_list = list(json_file[0].keys())[:-2] #局部变量，用于存放百科json文件的最外层父属性(院士名和百科名不计算)
    yuanshi_name = json_file[0]['院士名']
    align_res = process_entrace(key_list, baike_name, yuanshi_name)
    xiaoqi_res = xiaoqi.xiaoqi(yuanshi_name, align_res)
    return xiaoqi_res