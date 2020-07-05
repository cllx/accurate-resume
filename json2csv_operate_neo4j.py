import pandas as pd
import os
import sys
from SStack import SStack
from queue import Queue,LifoQueue
import json
import copy
from py2neo import Graph,Node,Relationship,cypher

test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')

# 获取指定目录下的json文件
def get_files(path='D:\zyt\\azyt\sfx', rule=".json"):
    all = []
    for fpathe,dirs,fs in os.walk(path):   # os.walk获取所有的目录
        for f in fs:
            filename = os.path.join(fpathe,f)
            if filename.endswith(rule):  # 判断是否是".json"结尾
                all.append(filename)
    return all

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
本函数用于处理倒数第二层属性并将其结果保存成dataframe
接受参数为维护的栈和队列，以及对应的院士名
当属性队列为空的时候，返回0
'''
def json_to_dataframe(st, key_queue, yuanshi_name_id):
    if not st.is_empty():
        content = set()
        word = st.pop() #弹出当前栈里面顶上的内容
        key_queue.put(word) #键值队列，用于保存前面已出现的键值(目的是方便后面迭代时能准确找到进行到什么地方了)
        attribute_value_list = [] #存储属性与值列表
        key_str = 'json_file'
        for j in key_queue.queue: #通过维护的键的队列取到对应的键值
            key_str += '[\''+j+'\']'
        #print("  ",key_str)
        attribute_value_list.append(eval(key_str))
        flag = 0 #标记这几个百科json文件的当前属性值是否为空
        for i in attribute_value_list:
            if type(i).__name__ == 'list': #处理百科json文件中该属性下的值如果是列表时的情况，则取出列表里的每一个字典
                flag = 1
                if word=='人物影响' or word=='研究领域' or word=='人才培养类' or word=='发明专利类' or word=='科研方向': #这三个属性的值没有子属性了，其值直接就是字符串形式，所以单独处理
                    res = process_string(word, i, yuanshi_name_id)
                    key = key_queue.get()
                    preserve_key_queue(key, key_queue)
                    json_to_dataframe(st, key_queue, yuanshi_name_id)
                else: #其他情况的属性值里还有子属性，此时如果是列表的话也是单独处理
                    res = process_list(word, i, yuanshi_name_id) #返回的是一个列表，列表里面是多个字典
                    key = key_queue.get()
                    preserve_key_queue(key, key_queue) #得到动态维护的键的队列
                    json_to_dataframe(st, key_queue, yuanshi_name_id)
                break
            elif type(i).__name__ == 'dict': #处理百科json文件中该属性下的值如果是字典时的情况，这里主要是针对单属性值
                flag = 1
                except_word = ['人物履历','教育经历','工作经历','成就']
                if word not in except_word:
                    res = process_dict(word, i, yuanshi_name_id)
                    key = key_queue.get()
                    preserve_key_queue(key, key_queue)
                    json_to_dataframe(st, key_queue, yuanshi_name_id)
                else: #当不是单属性值时，说明其还不是最外层的属性(也即为父属性)，则将其压入栈中后续出栈时再处理
                    dict_key1 = list(i.keys()) #将字典里的键都放入栈中，稍后依次取出进行对齐
                    dict_key1.reverse()
                    for i in dict_key1:
                        st.push(i)
                    json_to_dataframe(st, key_queue, yuanshi_name_id)
                break
            else:
                pass
        if flag==0: #表示这几个文件的当前属性都为空
            key = key_queue.get()
            preserve_key_queue(key, key_queue)
            json_to_dataframe(st, key_queue, yuanshi_name_id)
    else:
        return 0

''' 
用于查看当前的值是否已经存在于原dataframe里了，若存在则查看是否已经被连线过了
若没有连线，则添加一条边，若有连线则依次拥有相同值的下一个，若都有连线，则新加入一行
'''
def line2frame(word, content, yuanshi_name_id):
    global used_node_flag
    global count_property_id
    global used_node_flag #表示已使用过的节点集合
    global property_node
    global relation
    if content in property_node['name'].values: #如果当前处理的值在已有的dataframe已经存在
        relative_content_line = property_node.loc[property_node['name']==content] #在原有dataframe里找出所有该值对应的行
        flag = 0
        for i in relative_content_line['property_id'].values:
            if i in used_node_flag: #如果该id已经被处理过，则查看下一个
                continue
            else:
                yuanshi_count_temp_id = "yuanshi_"+str(yuanshi_name_id)
                new_relation_dict = {'from_id':yuanshi_count_temp_id, 'pro1':word, 'to_id':i}
                new_relation_line = pd.DataFrame(new_relation_dict,index=[0])
                relation = relation.append(new_relation_line,ignore_index=True)
                used_node_flag.append(i) #标志为已被处理过
                flag = 1 #表示找到了没被处理过的有相同值的行
                break
        if flag==0: #表示所有该值对应的行都被处理过
            write_to_dataframe(word, content, yuanshi_name_id, count_property_id)
            count_property_id += 1
        else:
            pass
    else:
        write_to_dataframe(word, content, yuanshi_name_id, count_property_id)
        count_property_id += 1
    
# 用于将处理结果存入dataframe里
def write_to_dataframe(word, content, yuanshi_name_id, to_id):
    global property_node
    global relation
    property_count_name_id = "property_"+str(to_id)
    new_node_dict = {'property_id':property_count_name_id, 'name':content}
    new_node_line = pd.DataFrame(new_node_dict,index=[0])
    yuanshi_count_temp_id = "yuanshi_"+str(yuanshi_name_id)
    new_relation_dict = {'from_id':yuanshi_count_temp_id, 'pro1':word, 'to_id':property_count_name_id}
    new_relation_line = pd.DataFrame(new_relation_dict,index=[0])
    property_node = property_node.append(new_node_line,ignore_index=True)
    relation = relation.append(new_relation_line,ignore_index=True)
    
#处理人物影响、研究领域时转化为dataframe的情况 
def process_string(word, attribute_value, yuanshi_name_id):
    content = ''
    for i in attribute_value:
        content += i
    if content == '':
        return 0
    line2frame(word, content, yuanshi_name_id)
    
# 处理其他除人物影响、研究领域外、人才培养外的list的情况
def process_list(word, attribute_value_list, yuanshi_name_id):
    if len(attribute_value_list) == 0:
        return ''
    keys = attribute_value_list[0].keys()
    list_key = ['院校','方向','荣誉','论著','散文类','项目','成果','发明专利类','事件','语录','职称']
    for i in attribute_value_list:
        content = ''
        if '所在单位' in keys:
            if i['所在单位']=='' and i['职称']=='':
                continue
            content = i['所在单位'] + i['职称']
            line2frame(word, content, yuanshi_name_id)
        elif '任免职位_职称' in keys:
            if i['任免职位_职称']=='':
                continue
            content = i['信息公布权威机关'] + i['任免职位_职称']
            line2frame(word, content, yuanshi_name_id)
        elif '演讲_报告题目' in keys:
            if i['组织单位_活动单位名称']=='' and i['演讲_报告题目']=='':
                continue
            content = i['组织单位_活动单位名称'] + i['演讲_报告题目']
            line2frame(word, content, yuanshi_name_id)
        else:
            for key in keys:
                if key in list_key:
                    if i[key]=='':
                        continue
                    content = i[key]
                    line2frame(key, content, yuanshi_name_id)

# 用于处理字典的情况
def process_dict(word, attribute_value_list, yuanshi_name_id):
    keys = attribute_value_list.keys()
    key_list = ['外文名','性别','出生日期','出生地','国籍','民族','职业','毕业院校','政治面貌','代表作品','主要成就','曾任职','信仰','原籍']
    for key in keys:
        content = ''
        if (key in key_list) and (type(attribute_value_list[key]).__name__ == 'dict'):
            content = attribute_value_list[key][key]
            #neo4j不能接收属性值为空的情况
            if content == '':
                continue
            if word=='基本信息':
                line2frame(key, content, yuanshi_name_id)
            else:
                line2frame(word, content, yuanshi_name_id)
        elif (key in key_list) and (type(attribute_value_list[key]).__name__ == 'list'):
            for i in attribute_value_list[key]:
                if word=='基本信息':
                    content = i[key]
                    #neo4j不能接收属性值为空的情况
                    if content == '':
                        continue
                    line2frame(key, content, yuanshi_name_id)
                else:
                    content = i[key]
                    #neo4j不能接收属性值为空的情况
                    if content == '':
                        continue
                    line2frame(word, content, yuanshi_name_id)
        else:
            pass

def process_entrace(key_list, yuanshi_name_id):
    st = SStack() #用栈存放每一轮的属性
    lq = LifoQueue(maxsize=0) #用后进先出队列用于存放文件操作过程中的中间键值(用于新建新的对齐json)
    key_list.reverse() #属性名列表反向，为了使最后按照正向的方式写入
    for i in key_list:
        st.push(i) #将最开始外层的属性名压入栈中
    res = json_to_dataframe(st, lq, yuanshi_name_id) #调用处理成dataframe的函数
    global property_node
    global relation
    global yuanshi_node
    property_node.to_csv('static/neo4j_csv/property_label.csv',index=False) #将df输出到csv文件，输出顺序为dataframe默认的列名顺序
    relation.to_csv('static/neo4j_csv/relation_label.csv',index=False)
    yuanshi_node.to_csv('static/neo4j_csv/yuanshi_label.csv',index=False)
    # 表示先删除当前已有的节点和关系
    cypher_delete = '''MATCH(b) detach delete b
                  '''
    test_graph.run(cypher_delete)
    # 表示加载属性到neo4j
    cypher_node = '''LOAD CSV WITH HEADERS FROM "http://localhost:5000/static/neo4j_csv/property_label.csv" AS line
                     MERGE (p:attribute{id:line.property_id,name:line.name})
                  '''
    test_graph.run(cypher_node)
    
    # 表示加载实体到neo4j
    cypher_node = '''LOAD CSV WITH HEADERS FROM "http://localhost:5000/static/neo4j_csv/yuanshi_label.csv" AS line
                     MERGE (p:yuanshi{id:line.yuanshi_id,name:line.name})
                  '''
    test_graph.run(cypher_node)
    
    # 表示加载关系到neo4j
    cypher_relation = '''LOAD CSV WITH HEADERS FROM "http://localhost:5000/static/neo4j_csv/relation_label.csv" AS line  
                         match (from:yuanshi{id:line.from_id}),(to:attribute{id:line.to_id})  
                         merge (from)-[r:rel{pro1:line.pro1}]->(to)
                      '''
    test_graph.run(cypher_relation)

def deal_yuanshinameid_and_in_process_entrnce(every_baike_json, json_file):
    global count_yuanshi_id
    global count_property_id
    global used_node_flag
    global yuanshi_node
    global property_node
    global relation
    used_node_flag = [] #定义一个列表，记录已使用节点
    key_list = list(json_file.keys()) #局部变量，用于存放百科json文件的最外层父属性(院士名和百科名不计算)
    yuanshi_name = every_baike_json['院士名']
    #取出属性数据集中的最后一行的数据
    last_property_line_value = property_node['property_id'][-1:].values[0] #取出当前属性集中已存在csv文件的最后一行节点的id号
    count_property_id = int(last_property_line_value.split("_")[1]) + 1 #由该id号的下一个数后开始进行增加
    
    #取出院士实体数据集中的最后一行数据
    last_yuanshi_line_value = yuanshi_node['yuanshi_id'][-1:].values[0] #取出当前属性集中已存在csv文件的最后一行节点的id号
    count_yuanshi_id = int(last_yuanshi_line_value.split("_")[1]) + 1 #由该id号的下一个数后开始进行增加
    
    #院士名这个节点单独处理，属性部分
    new_property_node = pd.DataFrame()
    count_property_temp_id = "property_"+str(count_property_id)
    new_property_node["property_id"] = [count_property_temp_id]
    new_property_node["name"] = [yuanshi_name]
    property_node = pd.concat([property_node, new_property_node], axis=0, ignore_index=True)
    
    #院士名这个节点单独处理，实体部分
    new_yuanshi_node = pd.DataFrame()
    count_yuanshi_temp_id = "yuanshi_"+str(count_yuanshi_id)
    new_yuanshi_node["yuanshi_id"] = [count_yuanshi_temp_id]
    new_yuanshi_node["name"] = [yuanshi_name]
    yuanshi_node = pd.concat([yuanshi_node, new_yuanshi_node], axis=0, ignore_index=True)
    
    #院士中文名这个关系单独处理
    new_relation = pd.DataFrame()
    new_relation["from_id"] = [count_yuanshi_temp_id]
    new_relation["pro1"] = ['中文名']
    new_relation["to_id"] = [count_property_temp_id]
    relation = pd.concat([relation, new_relation], axis=0, ignore_index=True)
    yuanshi_name_id = count_yuanshi_id #将院士名这个ID保存下来
    count_property_id += 1
    process_entrace(key_list, yuanshi_name_id)

def main(wait_deal_json):
    global yuanshi_node
    global property_node
    global relation
    global json_file #全局列表变量，用于存放不同百科json文件的内容
    yuanshi_node = pd.read_csv("static/neo4j_csv/yuanshi_label.csv")
    property_node = pd.read_csv("static/neo4j_csv/property_label.csv")
    relation = pd.read_csv("static/neo4j_csv/relation_label.csv")
    wait_deal_json = json.loads(wait_deal_json)
    json_file = wait_deal_json
    print("存入数据库前接收的参数:",json_file,type(json_file))
    deal_yuanshinameid_and_in_process_entrnce(wait_deal_json, json_file)