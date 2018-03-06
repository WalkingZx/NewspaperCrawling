# -*- coding: utf-8 -*-
import re
import json
import HTMLParser
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class CrawlerPipeline(object):
    def process_item(self, item, spider):
        return item

class NewsPipeline(object):

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

    def extract_county_from_bracket(self, str_):
        # s = '(Edinburgh, Scotland),'
        words = re.match(r'.*\((.*)\).*', str_)
        if words!=None:
            return words.group(1)
        else:
            return None

    def process_item(self, PageItem, spider):

        if spider.name == 'BNA':
            articles_in_page_count = len(PageItem['site'])
            for i in range(articles_in_page_count):
                site        = PageItem['site'][i]
                keyword     = PageItem['keyword'][i]
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
                
                article_item = ArticleItem(site = site, keyword= keyword, title=title, description=description, hint=hint, publish=publish, newspaper=newspaper, 
                    county=county, type_=type_, word=word, page=page, tag=tag)

                filename = site
                article_item.writeIntoJsonFile(filename)

        elif spider.name == 'GN':
            articles_in_page_count = len(PageItem['site'])
            for i in range(articles_in_page_count):
                site          = PageItem['site'][i]
                keyword       = PageItem['keyword'][i]
                reprint       = PageItem['reprints'][i]
                title         = PageItem['titles'][i]
                publish       = PageItem['publishs'][i]
                county        = self.extract_county_from_bracket(PageItem['counties'][i])
                word          = PageItem['words'][i]
                newspaper     = PageItem['newspapers'][i]
                download_page = PageItem['download_pages'][i]

                article_item = ArticleItem(site=site, keyword=keyword, reprint=reprint, title=title, publish=publish, county=county, word=word, newspaper=newspaper,
                    download_page=download_page)

                filename = site
                article_item.writeIntoJsonFile(filename)

        elif spider.name == 'WNO':
            # page['types'] = []
            # page['words'] = []
            # page['newspapers'] = []
            # page['pages'] = []
            # page['download_pages'] = []
            articles_in_page_count = len(PageItem['site'])
            for i in range(articles_in_page_count):
                site = PageItem['site'][i]
                keyword = PageItem['keyword'][i]
                title = PageItem['titles'][i]
                title = self.extract_words_from_line_break(title)
                publish = PageItem['publishs'][i]
                publish = self.extract_date_from_string(publish)
                description = PageItem['descriptions'][i]
                description = self.extract_words_from_line_break(description)
                # description = description.decode('unicode_escape')
                type_ = self.extract_words_from_line_break(PageItem['types'][i])
                words = self.extract_number_from_string(PageItem['words'][i])
                newspaper = self.extract_words_from_line_break(PageItem['newspapers'][i])
                page = self.extract_number_from_string(PageItem['pages'][i])
                download_page = PageItem['download_pages'][i]

                article_item = ArticleItem(site=site, keyword=keyword, title=title, publish=publish, description=description, type_=type_,
                    word=words, newspaper=newspaper, page=page, download_page=download_page)
                filename =site
                article_item.writeIntoJsonFile(filename)
            # articles_in_page_count = len(PageItem['newspapers'])
            # for i in PageItem['download_pages']:
            #     print i + '\n'

class ArticleItem:

    def __init__(self, title=None, keyword=None, description=None, hint=None, publish=None, newspaper=None, county=None, type_=None, word=None, page=None, tag=None,
        site=None, reprint=None, download_page=None, download_url=None):
        self.title = title
        self.keyword = keyword
        self.description = description
        self.hint = hint
        self.publish = publish
        self.newspaper = newspaper
        self.county = county
        self.type_ = type_
        self.word = word
        self.page = page
        self.tag = tag
        self.site = site
        self.reprint = reprint
        self.download_page = download_page
        self.download_url =download_url

    def writeIntoJsonFile(self, filename):
        with open("Crawler/Records/" + filename + ".json","a") as f:
            json.dump(self.__dict__ ,f)
            f.write(',\n')



             
