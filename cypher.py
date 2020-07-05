from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, flash, session, send_from_directory,make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from py2neo import Graph,Node,Relationship,cypher
from pandas import DataFrame
import random
import os
import json
from json_to_csv import json_to_csv
import update_align
import xiaoqi
from task_2 import auto_extract
app = Flask(__name__)

def get_files(path='static/TransE_img/', rule=".png"):
    all = []
    for fpathe,dirs,fs in os.walk(path):   # os.walk获取所有的目录
        for f in fs:
            filename = os.path.join(fpathe,f)
            if filename.endswith(rule):  # 判断是否是".png"结尾
                all.append(filename)
    return all

'''
这部分代码主要是为了将从neo4j数据库中的查询得到的结果转化成前端展示所需要的列表，
分别对应节点列表和边列表，两个列表分别对应各自需要的4个字段的字典
'''
def get_node_link(res):
    temp = res.iloc[:,:]
    for i in range(0,len(temp)):
        tmp = {}
        id_list = []
        for dic in node:
            id_list.append(dic['name']) #先把已有的name放到id_list里面，后面进行比较判断
        if temp.iloc[i]['Person']['id'] not in id_list: #如果当前头结点的没有在id_list里，就添加进去，并给name、label、category、value附上相应的值
            tmp['name'] = temp.iloc[i]['Person']['id']
            tmp['label'] = temp.iloc[i]['Person']['name']
            tmp['category'] = random.randint(1,10) #这里的category是随机赋的值
            tmp['value'] = random.randint(1,3) #这里的value也是随机赋的值
            node.append(tmp)
        tmp = {}
        if temp.iloc[i]['tail']['id'] not in id_list: #如果当前头结点的没有在id_list里，就添加进去，并给name、label、category、value附上相应的值
            tmp['name'] = temp.iloc[i]['tail']['id']
            tmp['label'] = temp.iloc[i]['tail']['name']
            tmp['category'] = random.randint(1,10)
            tmp['value'] = random.randint(1,3)
            node.append(tmp)
        rela = {}
        rela['source'] = temp.iloc[i]['Person']['id'] #记录下相应的边的头结点
        rela['target'] = temp.iloc[i]['tail']['id'] #记录下相应的边的尾节点
        rela['label'] = temp.iloc[i]['r']['pro1'] #记录下边的信息
        rela['value'] = random.randint(1,10) #value随机赋值
        link.append(rela)
    node_link['node'] = node
    node_link['link'] = link

#这个函数主要处理对齐结果的下载模块
@app.route('/get_align_json')
def get_align_json():
    return render_template('align_download.html') 

#这个函数主要从static里获取对齐处理的中间结果并展示到浏览器
@app.route('/align')
def align():
    filename = request.args.get('filename')
    filename = filename+'.json'
    fname = filename.encode('utf-8').decode('utf-8') #对要查询的名字进行编码、解码
    dirpath = 'static/align_json/'
    response = make_response(send_from_directory(dirpath, fname, as_attachment=True)) #将对应要查看的文件编码做成响应
    response.headers["Content-Disposition"] = "attachment; filename={}".format(dirpath.encode().decode('latin-1')) #添加头设置编码
    return send_from_directory(dirpath, fname) #添加头设置编码

#这个函数主要处理点击事件，使之跳转到消歧结果下载界面
@app.route('/get_xiaoqi_json')
def get_xiaoqi_json():
    return render_template('xiaoqi_download.html')

#这个函数主要从static里获取消歧处理的中间结果并展示到浏览器
@app.route('/xiaoqi')
def xiaoqi():
    filename = request.args.get('filename')
    filename = filename+'.json'
    fname = filename.encode('utf-8').decode('utf-8')
    dirpath = 'static/xiaoqi_json/reserve_score/'
    response = make_response(send_from_directory(dirpath, fname, as_attachment=True)) #将对应要查看的文件编码做成响应
    response.headers["Content-Disposition"] = "attachment; filename={}".format(dirpath.encode().decode('latin-1')) #添加头设置编码
    return send_from_directory(dirpath, fname) #发送到页面进行展示

#这个函数负责处理跳转到查询界面
@app.route('/get_query')
def get_relation_page():
    return render_template('query.html')

#这个函数主要负责处理查询院士的属性信息的部分，通过post接收要查询的属性，到neo4j进行搜索出相关结果，
#调用get_node_link函数转成两个列表的形式，将结果返回到index界面展示
@app.route('/get_attribute', methods=['GET', 'POST'])
def get_attribute():
    if request.method == 'POST':
        filename = request.form['filename']
        attribute = request.form["attribute"]
        global node
        global link
        global node_link
        node = []
        link = []
        node_link = {}
        test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
        query = "MATCH (Person {name:'"+filename+"'})-[r:rel{pro1:'"+attribute+"'}]->(tail) with Person,r,tail RETURN Person,r,tail" #查询院士的属性信息
        res = test_graph.run(query).data()
        res = DataFrame(res)
        get_node_link(res)
        if len(node_link['node'])==0 or len(node_link['link'])==0: #如果该院士对应的边或节点不存在的话，node_link为False
            node_link = False
            return render_template('yuanshi_map.html', yuanshi_info=node_link)
        node_link = json.dumps(node_link,ensure_ascii=False,indent=4)
        return render_template('index.html', yuanshi_info=node_link, filename=filename)

#这个函数查询院士之间关系，接收要查询的两个院士的名字，到neo4j查询结果，
#调用get_node_link转成前端展示需要的格式，返回到index页面展示
@app.route('/get_relation', methods=['GET', 'POST'])
def get_relation():
    if request.method == 'POST':
        filename1 = request.form['filename1']
        filename2 = request.form['filename2']
        global node
        global link
        global node_link
        node = []
        link = []
        node_link = {}
        test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
        query1 = "MATCH (Person {name:'"+filename1+"'})-[r]-(tail) with Person,r,tail return Person,r,tail" #查询院士1的信息
        query2 = "MATCH (Person {name:'"+filename2+"'})-[r]-(tail) with Person,r,tail return Person,r,tail" #查询院士2的信息
        res1 = test_graph.run(query1).data()
        res1 = DataFrame(res1)
        res2 = test_graph.run(query2).data()
        res2 = DataFrame(res2)
        get_node_link(res1) #调用get_node_link转成node列表和link列表
        get_node_link(res2) #调用get_node_link转成node列表和link列表
        node_link = json.dumps(node_link,ensure_ascii=False,indent=4) #node_link保存节点和边的对应信息
        return render_template('index.html', yuanshi_info=node_link, filename=filename1)

#这个函数负责跳转到最开始的单个院士查询界面
@app.route('/get_single_page')
def get_single_page():
    return render_template('single_person.html')

#通过post或get获取要查询的单个院士的名字，在neo4j数据库进行查询，
#调用get_node_link函数转换成前端展示需要的格式，将结果返回到index界面进行展示
@app.route('/single_info', methods=['GET', 'POST'])
def single_info():
    if request.method == 'POST':
        filename1 = request.form['filename']
        global node
        global link
        global node_link
        node = []
        link = []
        node_link = {}
        test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
        query = "MATCH (Person {name:'"+filename1+"'})-[r]-(tail) with Person,r,tail return Person,r,tail" #查询与某个院士的相关信息
        res = test_graph.run(query).data()
        res = DataFrame(res)
        get_node_link(res)
        node_link = json.dumps(node_link,ensure_ascii=False,indent=4)
        with open("/home/chenxl/data_mining_resume/static/select_history/selected_name.txt", "r") as f:
            lines = f.readlines()
            if (filename1+"\n") not in lines:
                lines.append(filename1+"\n")
            if len(lines) > 8:
                del(lines[0])
        with open("/home/chenxl/data_mining_resume/static/select_history/selected_name.txt", "w") as f:
            for line in lines:
                f.write(line)
        return render_template('index.html', yuanshi_info=node_link, filename=filename1, selected=lines)

'''
同上一个函数功能一样，不同的是不是通过表单接收参数的，而是通过get方式
获取要查询的单个院士的名字，在neo4j数据库进行查询，
调用get_node_link函数转换成前端展示需要的格式，将结果返回到index界面进行展示
'''
@app.route('/single_info2', methods=['GET', 'POST'])
def single_info2():
    filename = request.args.get('filename')
    #print("***********************", type(filename), filename)
    global node
    global link
    global node_link
    node = []
    link = []
    node_link = {}
    test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
    if isinstance(filename,str):
        query = "MATCH (Person {name:'"+filename+"'})-[r]-(tail) with Person,r,tail return Person,r,tail" #查询与某个院士的相关信息
    else:
        filename = filename['姓名']
        query = "MATCH (Person {name:'"+filename+"'})-[r]-(tail) with Person,r,tail return Person,r,tail" #查询与某个院士的相关信息
    #query = "MATCH (Person {name:'"+filename+"'})-[r]-(tail) with Person,r,tail return Person,r,tail" #查询与某个院士的相关信息
    res = test_graph.run(query).data()
    res = DataFrame(res)
    get_node_link(res)
    node_link = json.dumps(node_link,ensure_ascii=False,indent=4)
    return render_template('index.html', yuanshi_info=node_link, filename=filename)

#跳转到transE处理查询界面	
@app.route('/select_TransE')
def select_TransE():
    return render_template('transe_entreace.html')

'''
通过get获取要查询transE结果的院士的名字，首先在static里面该院士是否已经有
transE处理的相关结果了，如果有就直接展示已有的结果
如果没有就训练(调用json_to_csv转化成csv并调用transE模块处理)，并将结果展示
'''
@app.route('/transe_generate_deal_csv')
def transe_generate_deal_csv():
    filename = request.args.get('filename')
    imgname = filename+'.png'
    transeimg = get_files()
    for i in transeimg: #查看是否已经有训练好的TransE的图片了
        savedimg = i.split('/')[-1]
        if imgname==savedimg:
            respath = 'static/TransE_img/'+imgname
            return render_template('index.html', transe_res=respath, filename=filename)
    json2csv = json_to_csv()
    json2csv.main(filename) #调用json2csv将相关院士的数据转化为csv，再由TransE模块进行降维展示
    respath = 'static/TransE_img/'+imgname
    return render_template('index.html', transe_res=respath, tips='time_wait', filename=filename)

#负责从数据库中查询返回现在已有的院士，并将结果展示在前端
@app.route('/get_haved_yuanshi')
def get_haved_yuanshi():
    test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
    all_yuanshi = test_graph.run("MATCH (head)-[r:rel{pro1:'中文名'}]->(tail) RETURN head,r,tail;").data() #查询已有的院士的名字
    all_yuanshi = DataFrame(all_yuanshi)
    temp = all_yuanshi.iloc[:,:]
    yuanshi_list = []
    for i in range(0,len(temp)):
        tem = dict()
        tem['姓名'] = temp.iloc[i]['tail']['name']
        yuanshi_list.append(tem)
    all_yuanshi = test_graph.run("MATCH (head)-[r:rel{pro1:'性别'}]->(tail) RETURN head,r,tail;").data() #查询已有的院士的名字
    all_yuanshi = DataFrame(all_yuanshi)
    temp = all_yuanshi.iloc[:,:]
    for i in range(0,len(temp)):
        for j in yuanshi_list:
            if j['姓名'] == temp.iloc[i]['head']['name']:
                j['性别'] = temp.iloc[i]['tail']['name']
                break
    all_yuanshi = test_graph.run("MATCH (head)-[r:rel{pro1:'毕业院校'}]->(tail) RETURN head,r,tail;").data() #查询已有的院士的名字
    all_yuanshi = DataFrame(all_yuanshi)
    temp = all_yuanshi.iloc[:,:]
    for i in range(0,len(temp)):
        for j in yuanshi_list:
            if j['姓名'] == temp.iloc[i]['head']['name']:
                j['毕业院校'] = temp.iloc[i]['tail']['name']
                break
    all_yuanshi = test_graph.run("MATCH (head)-[r:rel{pro1:'出生地'}]->(tail) RETURN head,r,tail;").data() #查询已有的院士的名字
    all_yuanshi = DataFrame(all_yuanshi)
    temp = all_yuanshi.iloc[:,:]
    for i in range(0,len(temp)):
        for j in yuanshi_list:
            if j['姓名'] == temp.iloc[i]['head']['name']:
                j['出生地'] = temp.iloc[i]['tail']['name']
                break
    all_yuanshi = test_graph.run("MATCH (head)-[r:rel{pro1:'民族'}]->(tail) RETURN head,r,tail;").data() #查询已有的院士的名字
    all_yuanshi = DataFrame(all_yuanshi)
    temp = all_yuanshi.iloc[:,:]
    for i in range(0,len(temp)):
        for j in yuanshi_list:
            if j['姓名'] == temp.iloc[i]['head']['name']:
                j['民族'] = temp.iloc[i]['tail']['name']
                break
    all_yuanshi = test_graph.run("MATCH (head)-[r:rel{pro1:'出生日期'}]->(tail) RETURN head,r,tail;").data() #查询已有的院士的名字
    all_yuanshi = DataFrame(all_yuanshi)
    temp = all_yuanshi.iloc[:,:]
    for i in range(0,len(temp)):
        for j in yuanshi_list:
            if j['姓名'] == temp.iloc[i]['head']['name']:
                j['出生日期'] = temp.iloc[i]['tail']['name']
                break
    return render_template('all_yuansi_info.html', haved_yuanshi=yuanshi_list)

#负责跳转到get_new(生成新简历的界面)
@app.route('/get_new_yuanshi')
def get_new_yuanshi():
    return render_template('get_new.html')

'''
接收要生成简历的院士的名字，alignment_boshihou_pre_deal调用对齐处理
模块(假设已经爬取并抽取了其中的内容)生成对齐结果，对齐模块处理结果再调用
xiaoqi2.py进行消歧，xiaoqi2.py将处理的结果调用json2csv_operate_neo4j.py转化成csv并存入neo4j数据库
'''
@app.route('/generate_resume', methods=['GET', 'POST'])
def generate_resume():
    if request.method == 'POST':
        filename = request.form['filename']
        test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
        all_yuanshi_name = test_graph.run("MATCH (n:yuanshi) RETURN n").data() #查询已有的院士的名字
        all_yuanshi_name = DataFrame(all_yuanshi_name)
        temp = all_yuanshi_name.iloc[:,:]
        yuanshi_name_list = []
        for i in range(0,len(temp)):
            yuanshi_name_list.append(temp.iloc[i]['n']['name'])
        if filename in yuanshi_name_list:
            return render_template('transfer.html', filename=filename)
        else:
            extract_result = auto_extract.main_(filename)
            xiaoqi_res = update_align.main(extract_result) #调用对齐模块对要生成图谱的院士数据进行对齐
            print("***********消歧处理结果：",xiaoqi_res)
            global node
            global link
            global node_link
            node = []
            link = []
            node_link = {}
            test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
            query = "MATCH (Person {name:'"+filename+"'})-[r]-(tail) with Person,r,tail return Person,r,tail" #查询新生成的院士的数据
            res = test_graph.run(query).data()
            res = DataFrame(res)
            get_node_link(res)
            node_link = json.dumps(node_link,ensure_ascii=False,indent=4)
            return render_template('index.html', yuanshi_info=node_link, filename=filename, generate_resume="success")

'''
查询并返回所有的图谱
'''
@app.route('/get_all_yuanshi')
def get_all_yuanshi():
    global node
    global link
    global node_link
    node = []
    link = []
    node_link = {}
    test_graph = Graph('http://localhost:7474',username='neo4j',password='8611662')
    query = "MATCH (Person)-[r]->(tail) RETURN Person,r,tail" #查询所有数据的语句
    res = test_graph.run(query).data()
    res = DataFrame(res)
    get_node_link(res)
    node_link = json.dumps(node_link,ensure_ascii=False,indent=4)
    filename = '整个图谱'
    return render_template('index.html', yuanshi_info=node_link, filename=filename, generate_resume="success")

#flask代码的主函数，设置为debug = True可调式，多前程加快运行速度		
if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    #app.run(debug = True, threaded=True)
    app.run(host = "0.0.0.0", port=5000)