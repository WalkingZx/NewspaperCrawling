# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # Published = scrapy.Field()
    pass

class PageItem(scrapy.Item):
    """docstring for ArticleItem"""
    titles = scrapy.Field()
    descriptions = scrapy.Field()
    hints = scrapy.Field()
    publishs = scrapy.Field()
    newspapers = scrapy.Field()
    counties = scrapy.Field()
    types = scrapy.Field()
    words = scrapy.Field()
    pages = scrapy.Field()
    tags = scrapy.Field()
    download_pages = scrapy.Field()