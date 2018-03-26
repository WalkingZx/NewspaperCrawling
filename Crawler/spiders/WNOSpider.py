# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from bs4 import BeautifulSoup
from Crawler.items import PageItem
import re
import sys
import scrapy
import HTMLParser
import requests
import os
import csv
import urllib

reload(sys)  
sys.setdefaultencoding('utf-8')

class WNOSpider(Spider):
    name = "WNO"
    SITE_NAME = 'Wals News Lib WebSite'
    SEARCH_KEY_WORD_INFOS = []
    # url = 'http://newspapers.library.wales/search?range[min]=' + START_DATE + '&range[max]=' + END_DATE + '&query=' + SEARCH_KEY_WORD

    INPUT_FILENAME = 'Crawler/spiders/WNO_search_input.csv'

    if os.path.exists(INPUT_FILENAME):
        print '\nHad found the input file, reading now...\n'
        with open(INPUT_FILENAME,'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            SEARCH_KEY_WORD_INFOS = [row for row in reader]
    else:
        print '\nDid not find the input file, please check if thie file exists!\n'

    start_urls =[]
    for i in range(len(SEARCH_KEY_WORD_INFOS)):
        start_urls.append('http://newspapers.library.wales/search?range[min]=' + SEARCH_KEY_WORD_INFOS[i]['start_date(xxxx)'] + '&range[max]=' + SEARCH_KEY_WORD_INFOS[i]['end_date(xxxx)'] + '&query=' + SEARCH_KEY_WORD_INFOS[i]['keyword'] + '&page=1')

    headers = {
    "Accept"            :"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding"   :"gzip, deflate, br",
    "Accept-Language"   :"zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control"     :"max-age=0",
    "Connection"        :"keep-alive",
    "User-Agent"        :"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36"
    }

    def extract_info_from_url(self, str_):
        # s = '(Edinburgh, Scotland),'
        words = re.match(r'.*range\[min\]=(.*)&range\[max\]=(.*)&query=(.*)&.*', str_)
        if words!=None:
            keyword = words.group(3)
            if '+' in keyword:
                keyword = keyword.replace('+', ' ')
            return words.group(1), words.group(2), keyword
        else:
            return None

    def parse(self, response):
        this_url = response.url
        this_url=urllib.unquote(this_url).decode('utf-8', 'replace').encode('gbk', 'replace')
        s, t, r = self.extract_info_from_url(this_url)
        SEARCH_KEY_WORD = r
        START_DATE = s
        END_DATE = t

        print SEARCH_KEY_WORD
        page = PageItem()
        page['site'] = []
        page['keyword'] = []
        page['titles'] = []
        page['descriptions'] = []
        page['publishs'] = []
        page['types'] = []
        page['words'] = []
        page['newspapers'] = []
        page['pages'] = []
        page['download_pages'] = []
        page['ocrs'] = []
        page['start_date']= []
        page['end_date'] =[]

        data = response.body
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")

        all_title_text = soup.find_all('h2', class_ = 'result-title')
        for title_text in all_title_text:
            download_page = response.urljoin(title_text.a.get('href'))
            title = title_text.get_text()
            page['site'].append(self.SITE_NAME)
            page['keyword'].append(SEARCH_KEY_WORD)
            page['download_pages'].append(download_page)
            page['titles'].append(title)
            ocr = self.parse_detail(download_page)
            page['ocrs'].append(ocr)
            page['start_date'].append(START_DATE)
            page['end_date'].append(END_DATE)
            # yield scrapy.Request(url = download_page, headers = self.headers, callback = self.parse_detail, dont_filter=True)

        
        all_result_summary = soup.find_all('p', class_='result-summary')
        for result_smmary in all_result_summary:
            description = result_smmary.find('span', class_ = 'hidden-xs').get_text()
            page['descriptions'].append(description)

        all_result_meta = soup.find_all('ul', class_='result-meta row')
        for result_meta in all_result_meta:
            newspaper = result_meta.find('li', class_ = 'meta-title col-xs-6 col-sm-5 no-padding').a.string
            publish = result_meta.find('li', attrs = {'id' : 'result-meta-date'}).span.get_text()
            info = result_meta.find_all('li', class_ = 'col-sm-2 hidden-xs no-padding text-center')
            page_ = result_meta.find('li', class_ = 'col-sm-1 hidden-xs no-padding text-center').get_text()
            type_ = info[0].get_text()
            words = info[1].get_text()
            page['newspapers'].append(newspaper)
            page['publishs'].append(publish)
            page['pages'].append(page_)
            page['types'].append(type_)
            page['words'].append(words)

        pattern = re.compile('next page')
        next_page = soup.find('ul', class_= 'pagination')
        next_page_text = next_page.find(text=pattern).next_siblings
        next_button = None
        next_url = None
        for sibling in next_page_text:
            if 'li' in repr(sibling):
                next_button = repr(sibling)
                break;
        if next_button != None:
            try:
                next_url_info = next_button.split('"')
                next_url = next_url_info[1]
                if next_url:
                    print 'Next page loading ...'
                    h = HTMLParser.HTMLParser()
                    next_url = h.unescape(next_url)
                    yield scrapy.Request(next_url, callback=self.parse, headers=self.headers)
            except Exception as e:
                raise 'Error in getting next page!(WNOSpider)'

        yield page

    def parse_detail(self, url):
        print 'Parsing the detail page now...'
        html = requests.get(url, headers=self.headers)
        data = html.text
        soup = BeautifulSoup(data, "html.parser")
        get_id_detail = soup.find('div', attrs = {'id': 'article-panel-main'})
        id_str = get_id_detail.script.get_text()
        id_str = id_str.split("'")[1]
        this_OCR = soup.find('div', attrs = {'id' : id_str}).find('span', attrs = {'itemprop' : 'articleBody'}).get_text()
        return this_OCR
        
        # pass


            

