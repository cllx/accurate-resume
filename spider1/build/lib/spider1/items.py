# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Spider1Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    real_url = scrapy.Field()
    url_score = scrapy.Field()
    keywords = scrapy.Field()
    em_score = scrapy.Field()
    attribute = scrapy.Field()
    nums = scrapy.Field()
    flag = scrapy.Field()
    is_multi_value = scrapy.Field()
    disambiguate_id = scrapy.Field()
