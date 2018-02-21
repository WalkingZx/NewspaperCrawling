from scrapy.spiders import Spider
from bs4 import BeautifulSoup
from Crawler.items import PageItem
import re
import sys
import scrapy

reload(sys)  
sys.setdefaultencoding('utf-8')

class BNASpider(Spider):
    name = "BNA"
    base_url = 'https://www.britishnewspaperarchive.co.uk'
    start_urls = ['https://www.britishnewspaperarchive.co.uk/search/results?basicsearch=%22election%20riot%22&retrievecountrycounts=false&page=0']
    headers = {
    "Accept"            :"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding"   :"gzip, deflate, br",
    "Accept-Language"   :"zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control"     :"max-age=0",
    "Connection"        :"keep-alive",
    "Host"              :"www.britishnewspaperarchive.co.uk",
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
        # //*[@id="ajaxcontainer"]/div[3]/div/div[2]/article[1]/div[3]/footer/div/small/span[1]/text()
        # countries = scrapy.Field()
        # types = scrapy.Field()
        # words = scrapy.Field()
        # pages = scrapy.Field()
        # tags = scrapy.Field()
        page = PageItem()
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
        data = response.body
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        # print soup
        all_articles = soup.find_all("article", class_ = "bna-card")
        for article in all_articles:
            # To get the title text 
            this_title=article.find('h4', class_="bna-card__title")
            for title in this_title.stripped_strings:
                page['titles'].append(title)

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
        next_page_full_url = response.urljoin(next_page)
        yield scrapy.Request(next_page_full_url, callback=self.parse, headers=self.headers)


            

