# -*- coding: utf-8 -*-
from scrapy.spiders import Spider
from bs4 import BeautifulSoup
from Crawler.items import PageItem
import requests
import re
import sys
import scrapy
import json
import os
import csv

reload(sys)  
sys.setdefaultencoding('utf-8')

class BNASpider(Spider):

    Username = 'nick.vivyan@durham.ac.uk'
    Password = 'EV19@Nick'
    RememberMe = 'false'
    NextPage = ''

    name = "BNA"
    SEARCH_URL = 'https://www.britishnewspaperarchive.co.uk/search/results'
    LOGIN_URL = "https://www.britishnewspaperarchive.co.uk/account/login"
    SITE_NAME = 'britishnewspaperarchive'
    SEARCH_KEY_WORD_INFOS = []
    SLASH = '/'

    INPUT_FILENAME = 'Crawler/spiders/BNA_search_input.csv'
    if os.path.exists(INPUT_FILENAME):
        print '\nHad found the input file, reading now...\n'
        with open(INPUT_FILENAME,'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            SEARCH_KEY_WORD_INFOS = [row for row in reader]
    else:
        print '\nDid not find the input file, please check if thie file exists!\n'
    
    parse_urls = []
    for i in range(len(SEARCH_KEY_WORD_INFOS)):
        parse_urls.append(SEARCH_URL + SLASH + SEARCH_KEY_WORD_INFOS[i]['start day(xxxx-xx-xx)'] + SLASH + SEARCH_KEY_WORD_INFOS[i]['end day(xxxx-xx-xx)'] + '?basicsearch=' + SEARCH_KEY_WORD_INFOS[i]['keyword'] + '&retrievecountrycounts=false&page=0')

    headers = {
    "Accept"            :"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding"   :"gzip, deflate, br",
    "Accept-Language"   :"zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control"     :"max-age=0",
    "Connection"        :"keep-alive",
    "Host"              :"www.britishnewspaperarchive.co.uk",
    "User-Agent"        :"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36",
    "Origin"            :"https://www.britishnewspaperarchive.co.uk",
    "Link"              :"<https://www.britishnewspaperarchive.co.uk/account/login>; rel=\"canonical\"",
    "X-Frame-Options"   :"SAMEORIGIN",
    }

    # def stringToDict(self, cookies):
    #     itemDict = {}
    #     items = cookies.split(';')
    #     for item in items:  
    #         key = item.split('=')[0].replace(' ', '')
    #         value = item.split('=')[1]  
    #         itemDict[key] = value  
    #     return itemDict             

    def parse_next_page(self, response):
        data = response.body
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        next_page = soup.find(name = 'a', attrs = {'title':re.compile(r"Forward")})
        # print len(next_page)
        if next_page:
            return next_page['href']
        else:
            print 'Error'

    def start_requests(self):
        print '\nReady to login...\n'
        return [scrapy.FormRequest(url=self.LOGIN_URL,                           
                                headers = self.headers,
                                meta = {
                                    'dont_redirect': True,
                                    'handle_httpstatus_list': [302]
                                },  
                                formdata = {
                                'Username': self.Username,
                                'Password': self.Password,
                                'RememberMe': self.RememberMe,
                                'NextPage': self.NextPage
                                },
                                callback = self.after_login,
                                dont_filter=False
                                )]

    def after_login(self, response):
        print '\nAfter Login..\n'
        Cookie = response.headers.getlist('Set-Cookie')[0].split(';')[0].split('session_0=')[1]
        # Cookie = response.headers
        session_cookies = {'session_0':Cookie}
        if Cookie == '':
            print '\nNo Cookie, restart!\n'
        else:
            count = 0
            for url in self.parse_urls:
                yield scrapy.Request(url, meta={"keyword_count": count}, cookies = session_cookies, callback = self.parse_page)
                count = count + 1

    def parse_page(self, response):
        Cookie_str = response.request.headers.getlist('Cookie')[0].split(';')[0].split('session_0=')[1]
        session_cookies = {'session_0':Cookie_str}
        # Cookie = {'Cookie':Cookie_str}
        keyword_count = response.meta['keyword_count']
        print 'KeyWord Count:', keyword_count

        page = PageItem()
        page['site'] = []
        page['keyword'] = []
        page['titles'] = []
        page['hints'] = []
        page['descriptions'] = []
        page['publishs'] = []
        page['counties'] = []
        page['types'] = []
        page['words'] = []
        page['pages'] = []
        page['tags'] = []
        page['newspapers'] = []
        page['download_pages']= []
        page['download_urls'] = []
        page['ocrs'] = []
        page['start_date'] = []
        page['end_date'] = []

        # print response.headers.getlist('Set-Cookie')
        data = response.body
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        # Cookie = response.headers.getlist('Set-Cookie')
        # cookies = self.stringToDict(Cookie)
        # print soup
        all_articles = soup.find_all("article", class_ = "bna-card")
        for article in all_articles:
            # To get the title text 
            this_title=article.find('h4', class_="bna-card__title")

            article_detail_url = response.urljoin(this_title.find('a').get('href'))
            page['download_pages'].append(article_detail_url)
            download_url, ocr = self.parse_details(article_detail_url, headers = self.headers, cookies = session_cookies)
            page['download_urls'].append(download_url)
            page['ocrs'].append(ocr)
            # print download_url
            # print ocr
            # with open('detail.html', 'wb') as file:
                # file.write(html.content)
            # page_detail = self.parse_details(url = article_detail_url, cookies = cookies)

            for title in this_title.stripped_strings:
                page['titles'].append(title)
                page['site'].append(self.SITE_NAME)
                page['keyword'].append(self.SEARCH_KEY_WORD_INFOS[keyword_count]['keyword'])
                page['start_date'].append(self.SEARCH_KEY_WORD_INFOS[keyword_count]['start day(xxxx-xx-xx)'])
                page['end_date'].append(self.SEARCH_KEY_WORD_INFOS[keyword_count]['end day(xxxx-xx-xx)'])

            # To get the title text title tag
            this_title=article.find('h4', class_="bna-card__title")
            title_tag=this_title.find('a')
            this_title_all_attributes=title_tag.attrs
            this_title_title_attribute=this_title_all_attributes['title']
            page['hints'].append(this_title_title_attribute)

        all_description=soup.find_all('p', class_="bna-card__body__description")
        # all_description[0].find_all('p', class_="bna-card__body__description")
        for description in all_description:
            page['descriptions'].append(description.get_text())

        all_metas = soup.find_all('div', class_="bna-card__meta")
        # print all_metas[0].find_all('div', class_="bna-card__meta")
        for meta in all_metas:
            page['publishs'].append(meta.small.span.get_text())
            for item in meta.small.span.find_next_siblings("span"):
                item_str = item.get_text().encode('utf-8')
                if 'Newspaper' in item_str:
                    page['newspapers'].append(item_str.split('Newspaper:\n')[1])
                elif 'County' in item_str:
                    # print item_str.split(('County:\n')[1])
                    page['counties'].append(item_str.split('\nCounty: \r\n')[1])
                elif 'Type' in item_str:
                    page['types'].append(item_str.split('\nType:')[1])
                elif 'Word' in item_str:
                    # print item_str.split('\nWords: \r\n')
                    page['words'].append(item_str.split('\nWords: \r\n')[1])
                elif 'Page' in item_str:
                    # print item_str.split('\nPage:')
                    page['pages'].append(item_str.split('\nPage:')[1])
                elif 'Tag' in item_str:
                    # print item_str.split('\nTags:\n')
                    page['tags'].append(item_str.split('\nTags:\n')[1])
                else:
                    # print item_str
                    print 'Error'
        yield page

        next_page = self.parse_next_page(response)
        if next_page is not None:
            next_page_full_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_full_url, callback=self.parse_page, meta={"keyword_count": keyword_count},headers=self.headers)

    def parse_details(self, url, headers, cookies):
        link = url.split('bl')[1]
        # print ocr_link
        ocr_link = 'https://www.britishnewspaperarchive.co.uk/tags/itemocr/BL/' + link
        json_str = requests.get(ocr_link, cookies = cookies, headers=self.headers)
        json_str.encoding = 'gbk'
        json_str = json.loads(json_str.content)
        OCR_text = ''
        for j in json_str:
            OCR_text = OCR_text + j['LineText']
        # print OCR_text
        download_url = 'https://www.britishnewspaperarchive.co.uk/viewer/download/bl' + link
        return download_url, OCR_text





            

