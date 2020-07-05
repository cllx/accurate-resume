import json

def score(data):
	id_list = [] #消歧编号的集合
	flag_list = [] #消歧标记的集合

	attr_list = [] #打分之后的列表
	disambiguate = [] #消歧后的列表


	#把所有属性加入name_list
	for d in data:
		#print(d)
		if d['disambiguate_id'] not in id_list:
			id_list.append(d['disambiguate_id'])
			flag_list.append(d['flag'])

	#对于每一个消歧编号
	for i in id_list:
		attr_dict = {}
		nums_score = 0
		url_score = 0
		em_score = 0
		score = 0
		for d in data:
			if d['disambiguate_id'] == i:
				try:
					#计算搜索结果总数的分数
					nums_score = 1 if int(d['nums']) < 100 else 5 if int(d['nums']) >1000 else 3
				except:
					pass
				attr = d['attribute'] #关键字
				flag = d['flag'] #消歧标记
				is_multi_value = d['is_multi_value'] #是否多真值
				url_score += float(d['url_score'])
				em_score += float(d['em_score'])
		score = nums_score + url_score + em_score
		attr_dict['disambiguate_id'] = i
		attr_dict['attr'] = attr
		attr_dict['score'] = score
		attr_dict['flag'] = flag
		attr_dict['is_multi_value'] = is_multi_value
		attr_list.append(attr_dict)
	'''
	with open('score.json', 'w', encoding = 'utf-8') as f:
		json.dump(attr_list, f, ensure_ascii=False, indent = 4)
	'''
	#print(attr_list)
	
	#计算每个flag对应的总得分
	for i in set(flag_list):
		sum_score = 0
		for d in attr_list:
			if d['flag'] == i:
				sum_score += d['score']
		for d in attr_list:
			if d['flag'] == i:
				d['score'] = d['score'] / sum_score

	#处理单真值
	for i in set(flag_list):
		values = []
		for d in attr_list:
			#对于标志一样并且是单真值的属性
			if d['flag'] == i and d['is_multi_value'] == '0':
				values.append(d['score'])
		
		for d in attr_list:
			if d['flag'] == i and values != [] and d['score'] == max(values):
				disambiguate.append(d)
		
	#处理多真值
	for i in set(flag_list):
		for d in attr_list:
			#对于标志一样并且是多真值的属性
			if d['flag'] == i and d['is_multi_value'] == '1':
				disambiguate.append(d)

	return attr_list, disambiguate
