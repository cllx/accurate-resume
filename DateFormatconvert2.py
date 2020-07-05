class DateFormatHelper2():
	def str2date(str_date):
		str_date=str_date.strip() #将时间字符串进行切分
		year=0
		month=0
		day=0
		if(len(str_date)>11): #如果时间字符串长度大于11，只取前11个
			str_date=str_date[:11]
		if len(str_date)==4 or len(str_date)==5:
			str_date = str_date.strip()
			year = str_date[:4] #年份取前四个
			return year
		if(str_date.find('-')>0): #处理以"-"进行分割的时间字符串
			date_list = str_date.split('-')
			j=0
			for i in date_list:
				if j==0:
					year = i
					if(year.isdigit()):
						year=int(year)
					else:
						year=0
					j += 1
				elif j==1:
					month = i
					if(month.isdigit()):
						month=int(month)
					else:
						month=0
					j += 1
				else:
					day = i
					if(day.isdigit()):
						day=int(day)
					else:
						day=0
					j += 1
		elif(str_date.find('年')>0): #处理以"年"、"月"、"日"进行分割的情况
			year=str_date[:4]
			if(year.isdigit()):
				year=int(year)
			else:
				year=0
			month=str_date[5:str_date.rfind('月')]
			if(month.isdigit()):
				month=int(month)
			else:
				month=0
			day=str_date[str_date.rfind('月')+1:str_date.rfind('日')]
			if(day.isdigit()):
				day=int(day)
			else:
				day=0
		elif(str_date.find('/')>0): #处理以"/"进行分割的情况
			date_list = str_date.split('/')
			j=0
			for i in date_list:
				if j==0:
					year = i
					if(year.isdigit()):
						year=int(year)
					else:
						year=0
					j += 1
				elif j==1:
					month = i
					if(month.isdigit()):
						month=int(month)
					else:
						month=0
					j += 1
				else:
					day = i
					if(day.isdigit()):
						day=int(day)
					else:
						day=0
					j += 1
		elif(str_date.find('.')>0): #处理以"."进行分割的情况
			date_list = str_date.split('.')
			j=0
			for i in date_list:
				if j==0:
					year = i
					if(year.isdigit()):
						year=int(year)
					else:
						year=0
					j += 1
				elif j==1:
					month = i
					if(month.isdigit()):
						month=int(month)
					else:
						month=0
					j += 1
				else:
					day = i
					if(day.isdigit()):
						day=int(day)
					else:
						day=0
					j += 1
		elif len(str_date)==6:
			year = str_date[:4]
			if(year.isdigit()):
				year=int(year)
			else:
				year=0
			month = str_date[4:]
			if(month.isdigit()):
				month=int(month)
			else:
				month=0
		elif len(str_date)==8:
			year = str_date[:4]
			if(year.isdigit()):
				year=int(year)
			else:
				year=0
			month = str_date[4:6]
			if(month.isdigit()):
				month=int(month)
			else:
				month=0
			day = str_date[6:]
			if(day.isdigit()):
				day=int(day)
			else:
				day=0
		else:
			pass
		if year!=0 and month!=0 and day!=0:
			return '%s-%s-%s' % (year,month,day)
		elif year!=0 and month!=0 and day==0:
			return '%s-%s' % (year,month)
		elif year!=0 and month==0 and day==0:
			return '%s' % (year)
		else:
			return '%s-%s-%s' % (0,0,0)