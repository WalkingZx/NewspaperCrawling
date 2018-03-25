from scrapy.spiders import Spider
from bs4 import BeautifulSoup
from Crawler.items import PageItem
import re
import sys
import scrapy
import HTMLParser

reload(sys)  
sys.setdefaultencoding('utf-8')

class WNOSpider(Spider):
    name = "WNO"
    SITE_NAME = 'Wals News Lib WebSite'
    SEARCH_KEY_WORD = '"Election Riot"'

    url = 'http://newspapers.library.wales/search?range[min]=1804&range[max]=1919&query=' + SEARCH_KEY_WORD
    # advanced_url = url +  '&category[]='
    start_urls = [url]

        #if you want to go for a advanced search, you can add one parameter &category[]=, and the value
        #can be News, Detailed Lists, Results and Guides, Advertising, Family Notices
        #you can choose more than one value do your search, for example, 
        #http://newspapers.library.wales/search?range[min]=1804&range[max]=1919&query="Election Riot"&category[]=News&category[]=Advertising

    headers = {
    "Accept"            :"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding"   :"gzip, deflate, br",
    "Accept-Language"   :"zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control"     :"max-age=0",
    "Connection"        :"keep-alive",
    "User-Agent"        :"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36"
    }

    def parse_next_page(self, response):
        data = response.body
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        next_page = soup.find(name = 'a', attrs = {'title':re.compile(r"Forward")})
        # print len(next_page)
        if next_page:
            return next_page['href']
        else:
            print 'Error'

    def parse(self, response):
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

        data = response.body
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")

        all_title_text = soup.find_all('h2', class_ = 'result-title')
        for title_text in all_title_text:
            download_page = response.urljoin(title_text.a.get('href'))
            title = title_text.get_text()
            page['site'].append(self.SITE_NAME)
            page['keyword'].append(self.SEARCH_KEY_WORD)
            page['download_pages'].append(download_page)
            print download_page
            page['titles'].append(title)
            yield scrapy.Request(url = download_page, headers = self.headers, callback = self.parse_detail, dont_filter=True)
        
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

    def parse_detail(self, response):
        data = response.body
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        get_id_detail = soup.find('div', attrs = {'id': 'article-panel-main'})
        id_str = get_id_detail.script.get_text()
        id_str = id_str.decode("unicode-escape").encode('utf8').split("'")[1]
        this_ORC = soup.find('div', attrs = {'id' : id_str}).find('span', attrs = {'itemprop' : 'articleBody'})
        
        # pass

        # pattern = re.compile('next page')
        # next_page = soup.find('ul', class_= 'pagination')
        # next_page_text = next_page.find(text=pattern).next_siblings
        # next_button = None
        # next_url = None
        # for sibling in next_page_text:
        #     if 'li' in repr(sibling):
        #         next_button = repr(sibling)
        #         break;
        # if next_button != None:
        #     try:
        #         next_url_info = next_button.split('"')
        #         next_url = next_url_info[1]
        #         if next_url:
        #             h = HTMLParser.HTMLParser()
        #             next_url = h.unescape(next_url)
        #             yield scrapy.Request(next_url, callback=self.parse, headers=self.headers)
        #     except Exception as e:
        #         raise 'Error in getting next page!(WNOSpider)'

        # yield page

            

