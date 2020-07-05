#-*- coding:utf-8 -*-
import re
import os
def write_file(name,source,basic_information,character_experience,social_service,major_achievement):
    def write_file_1(information,start_label,cycle_label,end_label,delete):
        #信息写入函数
        f.write(start_label)
        if isinstance(information, dict):
        #如果输入是字典，则按字典的形式写入文件
            for key, value in information.items():
                print('{key}:{value}'.format(key=key, value=value))
                a = '{key}:{value}' + cycle_label
                f.write(a.format(key=key, value=value))
        else:
        #否则按照链表的形式写入文件
            print (information)
            for j in information:
                j = re.sub(delete, '', j)
                a = '%s' + cycle_label
                f.write(a %j)
        f.write(end_label)
    def mkdir(path):
        # 创建文件夹
        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")
        # 判断路径是否存在
        # 存在     True
        # 不存在   False
        isExists = os.path.exists(path)
        # 判断结果
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path)

            print (path + ' 创建成功')
            return True
        else:
            # 如果目录存在则不创建，并提示目录已存在
            print (path + ' 目录已存在')
            return False
    file_name = '院士信息' + '\\\\' + name + '\\\\' + name + '_' + source + '.txt '
    path = '院士信息' + '\\\\' + name
    mkdir(path)

    start_label = ['\t\t基本信息：\n\t\t\t','\t\t人物经历：\n\t\t\t','\t\t社会任职：\n\t\t\t','\t\t主要成就：\n\t\t\t']
    cycle_label = '\n\t\t\t' #循环写入时的一些格式要求
    end_label = '\n' #结束标识
    delete = '<>|\xa0|u201c|u201d'
    print(file_name)

    with open(file_name, 'a+', encoding='utf-8') as f:
        f.truncate(0)
        f.write('%s：\n' % name)  #first_title
        f.write('\t%s：\n'%source) #second_title
        write_file_1(basic_information,start_label[0],cycle_label,end_label,delete)
        write_file_1(character_experience,start_label[1],cycle_label,end_label,delete)
        write_file_1(social_service,start_label[2],cycle_label,end_label,delete)
        write_file_1(major_achievement,start_label[3],cycle_label,end_label,delete)
