 #-*- coding:utf-8 -*-
import os,sys 
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
sys.path.insert(0,parentdir)
import time
from bosonnlp import BosonNLP
from jieba import cut
import json
import re
import os
import os.path as op
import random
from task_2.Extract_job_infos.Extract_job_infos import main_han
#导入任务一的包
from task_1.baidu import baidu_extract
from task_1.sougou import sougou_extract
from task_1.hudong import hudong_extract
from task_1.bk360 import bk360_extract




# def words_cut(filename, isJieba=True):#分词，返回列表
#     text_cut = []
#
#     if isJieba:
#         with open(filename, 'r', encoding='utf-8') as f:#读文件
#             for line in f.readlines():
#                 line = line.strip()#去除空白符
#                 seg_line = cut(line)#返回的是生成器，只可遍历一遍
#                 line_str = " ".join(seg_line) + "\n"
#                 text_cut.append(line_str)
#         return text_cut
#
#     nlp = BosonNLP('QhCMB7FS.33943.0OYvhfw0JCx8')
#     with open(filename, 'r', encoding='utf-8') as f:
#         for line in f.readlines():
#             line_list = nlp.tag(line)[0]['word']#分词，返回一个嵌套的列表格式为[{'word':[分好的词], ''}]
#             line_str = " ".join(line_list)+'\n'#将列表连接为字符串
#             text_cut.append(line_str)
#     return text_cut

def words_cut(txt_lines, isJieba=True):#分词，返回列表
    text_cut = []
    if isJieba:
        for line in txt_lines:
            line = line.strip()#去除空白符
            seg_line = cut(line)#返回的是生成器，只可遍历一遍
            line_str = " ".join(seg_line) + "\n"
            text_cut.append(line_str)
        return text_cut

    nlp = BosonNLP('QhCMB7FS.33943.0OYvhfw0JCx8')
    for line in txt_lines:
        line_list = nlp.tag(line)[0]['word']#分词，返回一个嵌套的列表格式为[{'word':[分好的词], ''}]
        line_str = " ".join(line_list)+'\n'#将列表连接为字符串
        text_cut.append(line_str)
    return text_cut

def read_regex(filename):
    '''读取正则文件，返回一个字典'''
    with open(filename,'r',encoding='utf8') as f:
        dict_str = f.read()
        dict_ = eval(dict_str)
        return dict_

def read_academician(filename):
    '''读取爬取到的院士百科文件'''
    lines = []
    with open(filename,'r',encoding='utf-8') as f:
        for line in f.readlines():
            lines.append(line)
    return lines

def traversal(dict_, lines):
    '''遍历一个正则字典，抽取信息
    dict_:正则字典
    lines:待抽取的文本，用列表表示
    dic:字典，用于存储抽取出来的信息
    return: 一个字典，里面是抽出来的信息'''
    dict_result = {}
    for key, value in dict_.items():
        if isinstance(value,dict):#如果值是字典，递归遍历
            dict_result[key] = traversal(value, lines)#将返回的字典存入信息字典中，不破坏原来的结构
        elif isinstance(value,list):#否则，处理列表中的正则表达式
            list_result = []
            for rex in value:#1.取出每一个正则
                for line in lines:#2.取出文本的每一行
                    line = line.strip()#去掉开头和末尾的空白符
                    results = re.findall(rex, line)#3.进行匹配

                    if results:  # 4.如果匹配到结果
                        # print("result:", results)
                        for result in results:#5.对抽取出的每一个结果

                            if isinstance(result, tuple):#6.如果是元组，即该正则同时抽取出了时间和内容
                                if len(result) == 2:#只有一个时间点
                                    # print("2个值的结果：----",result)
                                    reslt = {}
                                    item = re.sub(r'\s*', '', result[0])  # 7.去除空白符
                                    if key in ['本科', '硕士研究生', '博士研究生']:
                                        reslt['时间'] = item
                                        item = re.sub(r'\s*', '', result[1])
                                        reslt['院校'] = item
                                    elif key == '主要荣誉':
                                        reslt['时间'] = item
                                        item = re.sub(r'\s*', '', result[1])
                                        reslt['荣誉'] = item
                                    elif key == '学术论著类':
                                        reslt['时间'] = item
                                        item = re.sub(r'\s*', '', result[1])
                                        reslt['论著'] = item
                                    elif key == '承担项目类':
                                        reslt['起始时间'] = ""
                                        reslt['终止时间'] = item#
                                        item = re.sub(r'\s*', '', result[1])
                                        reslt['项目'] = item
                                    elif key == '研究成果类':
                                        reslt['时间'] = item
                                        item = re.sub(r'\s*', '', result[1])
                                        reslt['成果'] = item
                                    elif key == "社会任职":
                                        reslt['起始时间'] = item
                                        reslt['终止时间'] = ""#
                                        item = re.sub(r'\s*', '', result[1])
                                        reslt['职称'] = item
                                    list_result.append(reslt)

                                if len(result) == 3:#是一个时间段，有起始时间和终止时间
                                    # print('3个值的结果----',result)
                                    reslt = {}
                                    item = re.sub(r'\s*', '', result[0])  # 7.去除空白符
                                    reslt['起始时间'] = item#
                                    item = re.sub(r'\s*', '', result[1])  # 7.去除空白符
                                    reslt['终止时间'] = item#
                                    if key in ['本科', '硕士研究生', '博士研究生']:
                                        item = re.sub(r'\s*', '', result[2])
                                        reslt['院校'] = item
                                    elif key == '主要荣誉':
                                        item = re.sub(r'\s*', '', result[2])
                                        reslt['荣誉'] = item
                                    elif key == '学术论著类':
                                        item = re.sub(r'\s*', '', result[2])
                                        reslt['论著'] = item
                                    elif key == '承担项目类':
                                        item = re.sub(r'\s*', '', result[2])
                                        reslt['项目'] = item
                                    elif key == '研究成果类':
                                        item = re.sub(r'\s*', '', result[2])
                                        reslt['成果'] = item
                                    elif key == "社会任职":
                                        item = re.sub(r'\s*', '', result[2])
                                        reslt['职称'] = item
                                    list_result.append(reslt)

                            if isinstance(result, str):#8.如果是字符串，即没有抽取出时间，只有内容
                                result = re.sub(r'\s*', '', result) # 9.去除空白符
                                if key == '学术论著类':
                                    result = {"时间":"", "论著":result}
                                if key == "主要荣誉":
                                    result = {"时间":"", "荣誉":result}
                                if key == "承担项目类":
                                    result = {"起始时间":"","终止时间":"", "项目":result}
                                if key == "研究成果类":
                                    result = {"时间":"", "成果":result}
                                if key == "社会任职":
                                    result = {"起始时间":"","终止时间":"", "职称":result}
                                list_result.append(result)

            dict_result[key] = list_result
        elif value == "null":#如果没有正则表达式
            dict_result[key] = ""
        else :#否则是单个正则表达式，进行抽取
            # print(key,":",value)
            k = 0#记录每条正则抽取出来的信息条数
            for line in lines:#对于每一个正则，遍历院士信息所有行，寻求匹配
                line = line.strip()#去除两端的空白符
                # print(line)
                result = re.findall(value,line)
                      
                if result:#如果匹配到结果
                    result = re.sub(r'\s*','',result[0])#去除空白符
                    k += 1
                    if k == 1:
                        dict_result[key] = result
                    elif k == 2:#如果抽取到多条结果就存到列表当中
                        dict_result[key] = [dict_result[key]]
                        dict_result[key].append(result)
                    else:
                        dict_result[key].append(result)
            if k == 0:#如果没有抽取到任何结果，则置空
                dict_result[key] = ""
    return dict_result

def save_dict(dict,filename):
    with open(filename,'w',encoding='utf-8') as f:
        json.dump(dict,f,ensure_ascii=False)

def save_cut(text_cut, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(text_cut)

def cutdir(path, dirname1, dirname2):
    #获取院士文件夹下所有的文件，进行分词
    text_list = []
    for root, dirs, files in os.walk(path):
        #默认为广度优先，root为当前目录，
        #dirs为当前目录下的目录，files为当前目录下的文件。
        # print(root,files)
        if files:
            for name in files:
                text_list.append(os.path.join(root, name))
    #对每一个文件进行分词
    for txt in text_list:
        print("cutting the file %s" % (txt))
        dirpath = op.dirname(txt)#获取txt的路径
        dirpath = dirpath.replace(dirname1, dirname2)
        if not op.exists(dirpath):#创建分词文件夹
            os.mkdir(dirpath)
        txtname = op.basename(txt)#获取最底层的名字（文件名）
        save_path = op.join(dirpath, txtname) #替换文件夹，将二者结合成新的路径
        text_cut = words_cut(txt)#分词
        save_cut(text_cut, save_path)#保存
        print("save the cutfile %s" % (save_path))
    print("一共对%s个文件进行了分词。" % (len(text_list)))

def extractdir(path, dirname1, dirname2):
    #获取所有已经分词的文件    
    text_list = []
    for root, dirs, files in os.walk(path):#默认为广度优先
        if files:
            for name in files:
                text_list.append(os.path.join(root, name))
    #读取正则表达式
    filename='/home/chenxl/data_mining_resume/task_2/regexpression.txt'
    dict_ = read_regex(filename)
    #信息抽取
    for txt in text_list:
        # print(txt)
        print("extracting the file %s" % (txt))
        dirpath = op.dirname(txt)#获取路径
        dirpath = dirpath.replace(dirname1, dirname2)
        # print(dirpath)
        if not op.exists(dirpath):#创建简历文件夹
            os.mkdir(dirpath)
        txtname = op.basename(txt)#获取最底层的名字（文件名）
        save_path = op.join(dirpath, txtname) #将二者结合成新的路径
        lines = read_academician(txt)
        dict_jiben = traversal(dict_, lines)
        work, time = main_han('./task_2/title_list.py', txt)
        dict_jiben["人物履历"]["工作经历"]["人物经历"] = work
        dict_jiben["人物履历"]["工作经历"]["任职经历"] = time
        save_dict(dict_jiben,save_path)
        print("save the resumefile %s" % (save_path))
    print("一共抽取了%s个文件。" % (len(text_list)))


def main_(name):
    '''name:院士的姓名'''
    reg_file = "/home/chenxl/data_mining_resume/task_2/regexpression.txt"
    info = {}
    #搜狗百科
    t1 = time.time()
    sougou = sougou_extract(name)#爬取信息
    t2 = time.time()
    # print("crawer_time:", t2 - t1)
    # print("sougou-raw:\n", sougou)
    t3 = time.time()
    sougou = words_cut(sougou, False)  # 分词处理
    t4 = time.time()
    # print("bosen_cut_time:", t4 - t3)

    t3 = time.time()
    words_cut(sougou)  # 分词处理
    t4 = time.time()
    # print("jieba_cut_time:", t4 - t3)
    # print("cut:\n", sougou)
    work = main_han(sougou)
    # print(work)
    sougou = traversal(read_regex(reg_file), sougou)  # 抽取信息
    sougou['人物履历']['工作经历']['博士后'] = ''
    sougou["人物履历"]["工作经历"]["任职"] = work
    sougou['人物履历']['工作经历']['任免_辞职'] = ''
    sougou["院士名"] = name
    sougou["百科名"] = "搜狗百科"
    # print("sougou:\n", sougou)
    info["sougou"] = sougou
    #with open(name+"sougou.json","w",encoding="utf8") as f:
    #    json.dump(sougou, f, indent=4, ensure_ascii=False)

    #百度百科
    t1 = time.time()
    baidu = baidu_extract(name)# 爬取信息
    # print("time:", time.time() - t1)
    # print("baidu-raw:\n", baidu)
    t0 = time.time()
    baidu = words_cut(baidu, False)#分词处理
    # print("baidu_cut:", baidu)
    # print("bosen_cut_time:", time.time() - t0)
    t0 = time.time()
    words_cut(baidu)#分词处理
    # print("jieba_cut_time:", time.time() - t0)
    t0 = time.time()
    work = main_han(baidu)#工作经历抽取
    # print("main_han_time:", time.time() - t0)
    # print(work)
    t0 = time.time()
    baidu = traversal(read_regex(reg_file), baidu)#抽取其它信息
    # print(baidu)
    # print("ours_time:", time.time() - t0)
    baidu['人物履历']['工作经历']['博士后'] = ''
    baidu["人物履历"]["工作经历"]["任职"] = work
    baidu['人物履历']['工作经历']['任免_辞职'] = ''
    baidu["院士名"] = name
    baidu["百科名"] = "百度百科"
    # print("baidu:\n", baidu)
    info["baidu"] = baidu
    #with open(name+"baidu.json","w",encoding="utf8") as f:
    #    json.dump(baidu, f, indent=4, ensure_ascii=False)

    # #互动百科
    t1 = time.time()
    hudong = hudong_extract(name)
    # print("time:", time.time() - t1)
    # print("hudong-raw:\n", hudong)
    t0 = time.time()
    hudong = words_cut(hudong, False)  # 分词处理
    # print("bosen_cut_time:", time.time() - t0)
    t0 = time.time()
    words_cut(hudong)  # 分词处理
    # print("jieba_cut_time:", time.time() - t0)
    # print("cut:\n", hudong)
    work = main_han(hudong)
    hudong = traversal(read_regex(reg_file), hudong)
    hudong['人物履历']['工作经历']['博士后'] = ''
    hudong["人物履历"]["工作经历"]["任职"] = work
    hudong['人物履历']['工作经历']['任免_辞职'] = ''
    hudong["院士名"] = name
    hudong["百科名"] = "互动百科"
    # print("hudong:\n", hudong)
    info["hudong"] = hudong
    #with open(name+"hudong.json","w",encoding="utf8") as f:
    #    json.dump(hudong, f, indent=4, ensure_ascii=False)

    #360百科
    t1 = time.time()
    bk360 = bk360_extract(name)
    # print("time:", time.time() - t1)
    # print("bk360-raw:\n", bk360)
    t0 = time.time()
    bk360 = words_cut(bk360, False)  # 分词处理
    # print("bosen_cut_time:", time.time() - t0)
    t0 = time.time()
    words_cut(bk360)  # 分词处理
    # print("jieba_cut_time:", time.time() - t0)
    # print("cut:\n", bk360)
    work = main_han(bk360)
    bk360 = traversal(read_regex(reg_file), bk360)
    bk360['人物履历']['工作经历']['博士后'] = ''
    bk360["人物履历"]["工作经历"]["任职"] = work
    bk360['人物履历']['工作经历']['任免_辞职'] = ''
    bk360["院士名"] = name
    bk360["百科名"] = "360百科"
    # print("360:\n", bk360)
    info["bk360"] = bk360
    #with open(name+"360.json","w",encoding="utf8") as f:
    #    json.dump(bk360, f, indent=4, ensure_ascii=False)
    
    with open(name+"info.json","w",encoding="utf8") as f:
        json.dump(info, f, indent=4, ensure_ascii=False)
    extract_result = [baidu, sougou, hudong, bk360]
    #print(extract_result)
    return extract_result
    # return info


def extract_from_file(raw_info_path, reg_file):

    #先获取院士文件夹下所有的文件，进行抽取
    text_list = []
    for root, dirs, files in os.walk(raw_info_path):#默认为广度优先，root为当前目录，
        #dirs为当前目录下的目录，files为当前目录下的文件。
        # print(root,files)
        if files:#如果文件目录不空
            for name in files:#遍历每一个文件
                text_list.append(os.path.join(root, name))#组合成新的文件名

    #对每一个文件进行分词与抽取
    for txt in text_list:
        print(txt+" 正在被处理...............")
        dirpath = op.dirname(txt)#获取txt的路径
        dirpath = dirpath.replace("原始院士信息", '抽取的院士信息')
        if not op.exists(dirpath):#创建新文件夹
            os.mkdir(dirpath)
        txtname = op.basename(txt)#获取最底层的名字（文件名）
        with open(txt, "r", encoding='utf-8') as f:#将文件内容读出来
            text = f.readlines()
        text_cut = words_cut(text, False)#分词处理，使用波森分词
        work = main_han(text_cut)#工作经历抽取
        extract_info = traversal(read_regex(reg_file), text_cut)#抽取其它信息
        extract_info['人物履历']['工作经历']['博士后'] = ''
        extract_info["人物履历"]["工作经历"]["任职"] = work
        extract_info['人物履历']['工作经历']['任免_辞职'] = ''

        extract_info["院士名"] = txtname.split("_")[0]


        if "360" in txtname:
            extract_info["百科名"] = "360百科"
        if "搜狗百科" in txtname:
            extract_info["百科名"] = "搜狗百科"
        if "互动百科" in txtname:
            extract_info["百科名"] = "互动百科"
        if "百度百科" in txtname:
            extract_info["百科名"] = "百度百科"

        
        #替换文件夹，将二者结合成新的路径
        save_path = op.join(dirpath, txtname).replace(".txt", ".json") 
        with open(save_path,"w",encoding="utf8") as f:
            json.dump(extract_info, f, indent=4, ensure_ascii=False)
        print("{}已保存！".format(txtname.replace(".txt", ".json")))