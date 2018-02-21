# -*- coding: utf-8 -*-
import re
import json
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

class BNAPipeline(object):

    def extract_words_from_hints(self, hints):
        p = re.compile('<[^>]+>')
        return p.sub("", hints)

    def extract_words_from_line_break(self, string_):
        return string_.replace('\n', '').strip()

    def extract_number_from_string(self, str_):
        new_str = re.findall(r"\d+", str_)[0]
        return new_str

    def extract_date_from_string(self, str_):
        # p = re.compile('Published:[\s+]')
        # str_ = p.sub("", str_).replace('Published:\r', '')
        return re.sub(r'\s+','', str_).replace('Published:', '')

    def process_item(self, PageItem, BNASpider):
        articles_in_page_count = len(PageItem['publishs'])
        for i in range(articles_in_page_count):
            title       = self.extract_words_from_line_break(PageItem['titles'][i])
            description = self.extract_words_from_line_break(PageItem['descriptions'][i])
            hint        = self.extract_words_from_hints(PageItem['hints'][i])
            publish     = self.extract_date_from_string(PageItem['publishs'][i])
            newspaper   = self.extract_words_from_line_break(PageItem['newspapers'][i])
            county      = self.extract_words_from_line_break(PageItem['counties'][i])
            type_       = self.extract_words_from_line_break(PageItem['types'][i])
            word        = self.extract_number_from_string(PageItem['words'][i])
            page        = self.extract_number_from_string(PageItem['pages'][i])
            tag         = self.extract_words_from_line_break(PageItem['tags'][i])
            
            article_item = ArticleItem(title, description, hint, publish, newspaper, county, type_, word, page, tag)
        
            with open("Crawler/Records/BNA.json","a") as f:
                json.dump(article_item.__dict__ ,f)
                f.write(',\n')
        # for x in article_items:
        #     for key in x.__dict__:
        #             print key + ':  ' + x.__dict__[key]


    #titles = scrapy.Field()
    # descriptions = scrapy.Field()
    # hints = scrapy.Field()
    # publishs = scrapy.Field()
    # newspapers = scrapy.Field()
    # counties = scrapy.Field()
    # types = scrapy.Field()
    # words = scrapy.Field()
    # pages = scrapy.Field()
    # tags = scrapy.Field()

class ArticleItem:
    def __init__(self, title, description, hint, publish, newspaper, county, type_, word, page, tag):
        self.title = title
        self.description = description
        self.hint = hint
        self.publish = publish
        self.newspaper = newspaper
        self.county = county
        self.type_ = type_
        self.word = word
        self.page = page
        self.tag = tag

             
