from scrapy.spiders import Spider
from bs4 import BeautifulSoup
from Crawler.items import PageItem
import re
import sys
import scrapy
import urllib2
import requests
from scrapy.http import Request, FormRequest

reload(sys)  
sys.setdefaultencoding('utf-8')

class GNSpider(Spider):
    name = "GN"
    SITE_NAME = 'Gale Website'
    SEACH_KEY_WORD = '"Election Riot"'

    headers = {
    "Accept"            :"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding"   :"gzip, deflate, br",
    "Accept-Language"   :"zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control"     :"max-age=0",
    "Connection"        :"keep-alive",
    "User-Agent"        :"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36"
    }

    def generator_cookie(self, cookies):
        lists = cookies[0].split(';')
        cookie = {}
        for i in lists:
            j = i.strip()
            j = j.split('=')
            cookie[j[0]] = j[1]
        return cookie

    def generator_search_dataItem(self, data):
        lists = data.split('&')
        data = {}
        data['limiterFieldValue(ML)'] = []
        for i in lists:
            j = i.strip()
            j = j.split('=')
            if j[0] in 'limiterFieldValue(ML)':
                data['limiterFieldValue(ML)'].append(j[1])
            else:
                data[j[0]] = j[1]
        return data       

    def login_forward(self, response):
        data = response.body
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        action = "https://login.ezphost.dur.ac.uk/Shibboleth.sso/SAML2/POST"
        RelayState = soup.find('input', attrs = {'name':'RelayState'}).get('value')
        SAMLResponse = soup.find('input', attrs = {'name':'SAMLResponse'}).get('value')
        Elements = {'RelayState' : RelayState,
                    'SAMLResponse' : SAMLResponse}

        # response = requests.post(action,data=Elements)
        # return response
        return [FormRequest(
                          url=action,
                          formdata = Elements,
                          callback=self.doSearch,
                          dont_filter=True
                          )]


    def goto_durham_login(self, response):
        data = response.body
        main_domain = 'https://shib.dur.ac.uk'
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        action = soup.find_all('div', class_ = 'login')[0].find('form').get('action')
        login_url = main_domain + action
        # print login_url
        # print response.headers
        return [FormRequest(
                          url=login_url,
                          formdata={
                              'j_username': 'mpjn11',
                              'j_password': 'Zx98426513',
                              '_eventId_proceed': ''
                          },
                          callback=self.login_forward,
                          # dont_filter=True
                          )]

    def _requests_to_follow(self, response):
            
            if not isinstance(response, HtmlResponse):
                return
            seen = set()
            for n, rule in enumerate(self._rules):
                links = [l for l in rule.link_extractor.extract_links(response) if l not in seen]
                if links and rule.process_links:
                    links = rule.process_links(links)
                for link in links:
                    seen.add(link)
                    r = Request(url=link.url, callback=self._response_downloaded)

                    r.meta.update(rule=n, link_text=link.text, cookiejar=response.meta['cookiejar'])
                    yield rule.process_request(r)

    def goto_durham_login_pre(self, response):
        data = response.body
        soup = BeautifulSoup(data, "html.parser", from_encoding="utf8")
        action_url = soup.find('form', attrs = {'name':'EZproxyForm'}).get('action')
        RelayState = soup.find('input', attrs = {'name':'RelayState'}).get('value')
        SAMLRequest = soup.find('input', attrs = {'name':'SAMLRequest'}).get('value')
        Elements = {'RelayState' : RelayState,
                    'SAMLRequest': SAMLRequest}

        return [FormRequest(
                            url = action_url,
                            formdata = Elements,
                            callback = self.goto_durham_login)]

    def start_requests(self):
        GN_site = 'http://find.galegroup.com.ezphost.dur.ac.uk/dvnw/start.do?prodId=DVNW&userGroupName=duruni'
        return [Request(url=GN_site, callback = self.goto_durham_login_pre)]

    def doSearch(self, response):
        cookie = response.request.headers.getlist('Cookie')
        url = 'http://find.galegroup.com.ezphost.dur.ac.uk/dvnw/basicSearch.do'
        data = 'inputFieldName(0)=ke&inputFieldValue(0)=stchad&allbox=on&limiterFieldValue(ML)=Bbcn\
                &limiterFieldValue(ML)=Ncuk-1&limiterFieldValue(ML)=Bncn-1&limiterFieldValue(ML)=Bncn-2&limiterFieldValue(ML)=Bncn-3\
                &limiterFieldValue(ML)=Bncn-4&limiterFieldValue(ML)=Dmha&limiterFieldValue(ML)=Econ&limiterFieldValue(ML)=Ftha\
                &limiterFieldValue(ML)=Iln&limiterFieldValue(ML)=Inda-1 Or Inda-2&limiterFieldValue(ML)=Lsnr&limiterFieldValue(ML)=Pipo\
                &limiterFieldValue(ML)=Ttda-1 Or Ttda-2&limiterFieldValue(ML)=Tlsh&limiterType(ML)=OR&searchType=BasicSearchForm\
                &sgHitCountType=None&userGroupName=duruni&prodId=DVNW&startYear=1604&endYear=2016&isWhatsNewAvailable=&TAB1=&TAB2=\
                &ALTERNATE_TAB=&userGroupISBN=&method=doSearch&allLimiters='
        cookie = self.generator_cookie(cookie)
        data = self.generator_search_dataItem(data)
        data['inputFieldValue(0)'] = self.SEACH_KEY_WORD
        return [FormRequest(
                            url = url,
                            cookies = cookie,
                            headers = self.headers,
                            formdata = data,
                            callback = self.parse)]   

    def parse(self, response):
        # filename = 'search.html'
        # with open(filename, 'w') as f:
        #     f.write(response.body)
        cookie = response.request.headers.getlist('Cookie')
        data = response.body
        soup = BeautifulSoup(data, 'html.parser', from_encoding='utf-8')
        page = PageItem()
        page['site'] = []
        page['keyword'] = []
        page['reprints'] = []
        page['titles'] = []
        page['publishs'] = []
        page['counties'] = []
        page['words'] = []
        page['newspapers'] = []
        page['download_pages'] = []

        all_articles = soup.find_all('li', class_ = 'resultInfo')
        all_reprint = soup.find_all('li', class_ = 'collectionName')
        for reprint in all_reprint:
            page['reprints'].append(reprint.i.get_text())
        for article in all_articles:
            page['site'].append(self.SITE_NAME)
            page['keyword'].append(self.SEACH_KEY_WORD)
            page['titles'].append(article.p.b.a.spcitation.get_text())
            newspaper, county, text = article.find('span', class_ = 'txt_Detail').stripped_strings
            page['counties'].append(county)
            page['newspapers'].append(newspaper)
            text_info = re.match(r'(.*)\((\d+).*\).*', text)
            if text_info!=None:
                page['publishs'].append(text_info.group(1))
                page['words'].append(text_info.group(2))
            else:
                page['publishs'].append('')
                page['words'].append('')
            download_page = response.urljoin(article.p.b.a.get('href'))
            page['download_pages'].append(download_page)

        yield page

        next_page = soup.find('a', attrs = {'title' : 'Next'})
        if next_page is not None:
            next_page = next_page.get('href')
            next_page_full_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_full_url, callback=self.parse, headers=self.headers)
            # downlad = self.parse_downloadPage(url = download_page, cookies = cookie)

    # def parse_downloadPage(self, url, cookies):
    #     headers = self.headers
    #     cookies= self.generator_cookie(cookies)
    #     response = requests.get(url, headers = headers, cookies = cookies)
    #     filename = 'download.html'
    #     with open(filename, 'w') as f:
    #         f.write(response.text)









