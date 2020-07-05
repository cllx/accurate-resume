import scrapy
from spider1.items import Spider1Item
import re as regular
import requests
import urllib.parse
import string

#读文件（要搜索的三元组）
with open('keywords.txt', 'r', encoding='utf-8-sig') as f1:
	data = f1.readlines()

#读文件（域名和置信度）
with open('yuming.txt', 'r') as f2:
	yuming = f2.readlines()

class DmozSpider(scrapy.Spider):
	name = "spider1"
	#start_urls = [url_prefix.format(i) for i in range(0, 20, 10)]
	#定义爬虫url列表
	def start_requests(self):
		urls = []
		for d in data:
			d = d.strip('\n') # d:潘云鹤 1991-9-1994-7浙江大学计算机系 主任|102 0 5
			#d = d.rstrip(string.digits)
			kv = d.split('|') # kv[0] = 潘云鹤 1991-9-1994-7浙江大学计算机系 主任, kv[1] = 102 0 5
			#name = kv[0]
			#key = kv[1]
			#value = kv[2]
			for page in range(0, 100, 10):
				#url_prefix = "https://www.baidu.com/s?wd={name}%20{key}%20{value}&pn={page}".format(name = name, key = key, value = value, page = page)
				url_prefix = "https://www.baidu.com/s?wd={kv}&pn={page}".format(kv = kv[0], page = page)
				urls.append(url_prefix)
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	#定义回调函数
	def parse(self, response):
		item = Spider1Item()	
		attribute = regular.findall(r"wd=(.+?)&pn=", response.url)
		attribute = urllib.parse.unquote(attribute[0])
		print('现在在爬的属性是', attribute)
		
		for d in data:
			d = d.strip('\n')
			if attribute in d:
				kv = d.split('|')
				number = kv[1].split(' ')
				item['flag'] = number[0]
				item['is_multi_value'] = number[1]
				item['disambiguate_id'] = number[2]

		item['attribute'] = attribute
		page_now = regular.findall(r"&pn=(.+?)", response.url)
		print('现在的页数是', page_now[0])
		if int(page_now[0]) == 0:		
			# 取出获取到的总条数
			num = response.xpath('//*[@id="container"]/div[2]/div/div[2]/span').extract()
			try:
				num = num[0].replace(',', '')
				nums = regular.findall("\d+",num)
				item['nums'] = nums[0]
			except:
				pass

		re =  response.css('div.c-container')
		for r in re:			
			# 筛出url 获取真实url
			url = r.css('a::attr(href)').extract_first()
			try:
				get_url = requests.get(url, allow_redirects=False)
			except:
				print('error')
			if get_url.status_code == 200:
				real_url = re.search(r'URL=\'(.*?)\'', get_url.text.encode('utf-8'), re.S)
				print('真实的URL是'+real_url)
			elif get_url.status_code == 302:
				real_url = get_url.headers.get('location')
				print('真实的URL是'+real_url)
			item['real_url'] = real_url

			#给url打分，从文件读域名置信度，不在文件中的置信度为0.1分
			confidence = {}
			for d in yuming:
				d = d.strip('\n')
				a = d.split(' ')
				confidence[a[0]] = a[1]			
			url_score = 0
			for c in confidence:
				if c in real_url:
					url_score = confidence[c]
			if url_score != 0:
				print('该网页置信度为', url_score)
				#conf += float(score)
			else:
				url_score = 0.1
				print('该网页置信度为', url_score)
				#conf += 0.1
			item['url_score'] = url_score

			# 获取标红的关键字
			em = r.css('div.c-abstract em')
			keywords = em.css('::text').extract()
			if keywords == []:
				span = r.css('div.c-span-last em')
				keywords = span.css('::text').extract()
			print('关键词为', keywords)
			item['keywords'] = keywords

			#关键词打分 >=3个 0.1分 否则0分
			em_score = 0.1 if len(keywords) >= 3 else 0
			item['em_score'] = em_score
			print('关键词得分', em_score)

			yield item
