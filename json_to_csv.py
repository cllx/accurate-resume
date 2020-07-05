import pandas as pd
import os
import sys
from SStack import SStack
from queue import Queue,LifoQueue
import json
import copy
from py2neo import Graph,Node,Relationship,cypher
from en_re_pre_process import en_re_pre_process
import pca

class json_to_csv():
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
	def json_to_dataframe(self, st, key_queue):
		if not st.is_empty():
			content = set()
			word = st.pop() #弹出当前栈里面顶上的内容
			key_queue.put(word) #键值队列，用于保存前面已出现的键值(目的是方便后面迭代时能准确找到进行到什么地方了)
			attribute_value_list = [] #局部列表变量，用于存储不同百科文件当前属性下的值
			key_str = 'json_file'
			for j in key_queue.queue: #通过维护的键的队列取到对应的键值
				key_str += '[\''+j+'\']'
			#print("  ",key_str)
			attribute_value_list.append(eval(key_str))
			flag = 0 #标记这几个百科json文件的当前属性值是否为空
			for i in attribute_value_list:
				if type(i).__name__ == 'list': #处理百科json文件中该属性下的值如果是列表时的情况，则取出列表里的每一个字典
					flag = 1
					if word=='人物影响' or word=='研究领域' or word=='人才培养类': #这两个属性的值没有子属性了，其值直接就是字符串形式，所以单独处理
						res = self.process_string(word, i)
						key = key_queue.get()
						self.preserve_key_queue(key, key_queue)
						self.json_to_dataframe(st, key_queue)
					else: #其他情况的属性值里还有子属性，此时如果是列表的话也是单独处理
						res = self.process_list(word, i) #返回的是一个列表，列表里面是多个字典
						key = key_queue.get()
						self.preserve_key_queue(key, key_queue) #得到动态维护的键的队列
						self.json_to_dataframe(st, key_queue)
					break
				elif type(i).__name__ == 'dict': #处理百科json文件中该属性下的值如果是字典时的情况，这里主要是针对单属性值
					flag = 1
					except_word = ['人物履历','教育经历','工作经历','成就']
					if word not in except_word:
						res = self.process_dict(word, i)
						key = key_queue.get()
						self.preserve_key_queue(key, key_queue)
						self.json_to_dataframe(st, key_queue)
					else: #当不是单属性值时，说明其还不是最外层的属性(也即为父属性)，则将其压入栈中后续出栈时再处理
						dict_key1 = list(i.keys()) #将字典里的键都放入栈中，稍后依次取出进行对齐
						dict_key1.reverse()
						for i in dict_key1:
							st.push(i)
						self.json_to_dataframe(st, key_queue)
					break
				else:
					pass
			if flag==0: #表示这几个文件的当前属性都为空
				key = key_queue.get()
				self.preserve_key_queue(key, key_queue)
				self.json_to_dataframe(st, key_queue)
		else:
			return 0

	# 专门用于处理将结果添加到两个dataframe里
	def line2frame(self, word, content):
		global count_id
		global node 
		global relation
		new_node_dict = {'id':count_id, 'name':content}
		new_node_line = pd.DataFrame(new_node_dict,index=[0])
		new_relation_dict = {'from_id':1, 'pro1':word, 'to_id':count_id}
		new_relation_line = pd.DataFrame(new_relation_dict,index=[0])
		node = node.append(new_node_line,ignore_index=True)
		relation = relation.append(new_relation_line,ignore_index=True)
		count_id += 1
		
	#处理人物影响、研究领域时转化为dataframe的情况
	def process_string(self, word, attribute_value):
		content = attribute_value[0]
		#for i in attribute_value:
		#	content += i
		self.line2frame(word, content)
		
	# 处理其他除人物影响、研究领域外的list的情况
	def process_list(self, word, attribute_value_list):
		keys = attribute_value_list[0].keys()
		list_key = ['院校','方向','荣誉','论著','散文名称','项目','成果','专利名称','事件','语录','职称']
		for i in attribute_value_list:
			content = ''
			if '所在单位' in keys:
				if i['所在单位']=='' and i['职称']=='':
					continue
				content = i['所在单位'] + i['职称']
				self.line2frame(word, content)
			elif '任免职位_职称' in keys:
				if i['任免职位_职称']=='':
					continue
				content = i['信息公布权威机关'] + i['任免职位_职称']
				self.line2frame(word, content)
			elif '所在单位' in keys:
				if i['所在单位']=='' and i['职位_职称']:
					continue
				content = i['所在单位'] + i['职位_职称']
				self.line2frame(word, content)
			elif '演讲_报告题目' in keys:
				if i['组织单位_活动单位名称']=='' and i['演讲_报告题目']:
					continue
				content = i['组织单位_活动单位名称'] + i['演讲_报告题目']
				self.line2frame(word, content)
			else:
				for key in keys:
					if key in list_key:
						if i[key]=='':
							continue
						content = i[key]
						self.line2frame(key, content)

	# 用于处理字典的情况
	def process_dict(self, word, attribute_value_list):
		keys = attribute_value_list.keys()
		key_list = ['外文名','性别','出生日期','出生地','国籍','民族','职业','毕业院校','政治面貌','代表作品','主要成就','曾任职','信仰','原籍']
		for key in keys:
			content = ''
			if (key in key_list) and (type(attribute_value_list[key]).__name__ == 'dict'):
				content = attribute_value_list[key][key]
				if word=='基本信息':
					self.line2frame(key, content)
				else:
					self.line2frame(word, content)
			elif (key in key_list) and (type(attribute_value_list[key]).__name__ == 'list'):
				for i in attribute_value_list[key]:
					if word=='基本信息':
						content = i[key]
						self.line2frame(key, content)
					else:
						content = i[key]
						self.line2frame(word, content)
			else:
				pass

	def process_entrace(self, key_list, filename):
		st = SStack() #用栈存放每一轮的属性
		lq = LifoQueue(maxsize=0) #用后进先出队列用于存放文件操作过程中的中间键值(用于新建新的对齐json)
		key_list.reverse() #属性名列表反向，为了使最后按照正向的方式写入
		for i in key_list:
			st.push(i) #将最开始外层的属性名压入栈中
		res = self.json_to_dataframe(st, lq) #调用处理成dataframe的函数
		global node
		global relation
		path_node = 'static/yuanshi_csv/'+filename+'_node.csv'
		path_relation = 'static/yuanshi_csv/'+filename+'_relation.csv'
		node.to_csv(path_node, index=False)   #将df输出到csv文件，输出顺序为dataframe默认的列名顺序
		relation.to_csv(path_relation, index=False)

	def main(self, filename):
		global json_file #全局列表变量，用于存放不同百科json文件的内容
		global node
		global relation
		global count_id
		dirpath = 'static/xiaoqi_json/'+filename+'.json' #读取对应院士的消歧后的文件，接下来会把消歧后的文件转化为CSV
		with open(dirpath,'r',encoding='utf-8') as f: #打开json文件并保存到json文件列表里
			every_baike_json = json.load(f)
			json_file = every_baike_json
		key_list = list(json_file.keys()) #局部变量，用于存放百科json文件的最外层父属性(院士名和百科名不计算)，这里不取前两个是因为不考虑研究领域和获奖争议
		yuanshi_name = every_baike_json['院士名']
		count_id = 1
		first_node = {'id':1,'name':yuanshi_name} #初始化节点列表第一个节点
		node = pd.DataFrame(first_node,index=[0])
		first_relation = {'from_id':1,'pro1':'中文名','to_id':count_id} #初始化边列表的第一条边
		relation = pd.DataFrame(first_relation,index=[0])
		count_id += 1
		self.process_entrace(key_list, filename) #调用process_entrace开始处理转化为CSV(不同的实体用不同的id序号表示，对应的边的实体信息也用id序号表示)
		re_pre = en_re_pre_process()
		re_pre.pre_process(filename)
		pca.main(filename)