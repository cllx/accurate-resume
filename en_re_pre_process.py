import pandas as pd
import transE

class en_re_pre_process():
	#这个函数的主要作用是将原来的院士节点csv文件(关系文件)的name列和id列互换位置，并存入entity2id.txt(relation2id.txt)的文件中
	def pre_process(self, filename):
		print(filename)
		path1 = r'static/yuanshi_csv/'+filename+'_node.csv'
		path1 = path1.encode('utf-8').decode('utf-8')
		node = pd.read_csv(path1, engine='python', encoding='utf-8') #读取刚刚保存成的院士的CSV节点文件
		cols = list(node)
		cols.insert(0,cols.pop(cols.index('name')))
		node = node.loc[:,cols]
		path2 = r'static/TransE_shuju/'+filename.encode('utf-8').decode('utf-8')+'_entity2id.txt'
		node.to_csv(path2, sep='\t',index=False, header=None, encoding='UTF-8-sig')

		path3 = 'static/yuanshi_csv/'+filename+'_relation.csv'
		relation = pd.read_csv(path3,engine='python',encoding='utf-8')
		rela = relation[['pro1']]
		rela_name = set()
		for i in rela['pro1']:
			rela_name.add(i) #集合自动去除重复的关系
		string = ''
		rela_id = 0
		for i in rela_name:
			string = string+i+'\t'+str(rela_id)+'\n' #先以字符串的形式记录，稍后保存
			rela_id += 1 #不重复的关系id自动加1
		path4 = 'static/TransE_shuju/'+filename+'_relation2id.txt'
		with open(path4,"w",encoding="UTF-8-sig") as f:
			f.write(string)

		path5 = 'static/yuanshi_csv/'+filename+'_relation.csv'
		en_relation = pd.read_csv(path5,engine='python',encoding='utf-8')
		cols = list(en_relation)
		cols.insert(1,cols.pop(cols.index('to_id'))) #这是为了将尾实体和关系交换位置，方便后面TransE的处理
		en_relation = en_relation.loc[:,cols]
		entity_id = node.set_index('id').T.to_dict('list')
		# 对于每一行，通过列名name访问对应的元素
		for i in range(0, len(en_relation)):
			en_relation.loc[i,'from_id'] = entity_id[en_relation.iloc[i]['from_id']][0] #将对应的以id表示的头实体和尾实体用其实际字符表示
			en_relation.loc[i,'to_id'] = entity_id[en_relation.iloc[i]['to_id']][0] #将对应的以id表示的头实体和尾实体用其实际字符表示
		path6 = 'static/TransE_shuju/'+filename+'_train.txt' #存入到训练数据集中
		en_relation.to_csv(path6, sep='\t',index=False, header=None, encoding='UTF-8-sig')
		transE.main(filename) #调用TransE进行训练