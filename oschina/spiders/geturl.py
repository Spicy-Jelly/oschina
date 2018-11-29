# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from oschina.items import OschinaItem
import json, re, time, logging


logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class GeturlSpider(Spider):
    '''
        爬取开源中国（www.oschina.net）里的url
    '''
    name = 'geturl'
    allowed_domains = ['www.oschina.net']
    start_urls = ['https://www.oschina.net/']
    base_url = 'https://www.oschina.net'

    blog_article_page = 1  # 博客文章加载页码
    blog_article_base_url = 'https://www.oschina.net/blog/widgets/_blog_index_recommend_list?classification=0&p=' \
                            '{page}' \
                            '&type=ajax'


    def start_requests(self):
        yield Request(url=self.base_url, callback=self.parse_html)
        yield Request(url=self.base_url, callback=self.parse_header)
        # yield Request(url='https://www.oschina.net/project', callback=self.parse_project)
        # yield Request(url=self.blog_article_base_url.format(page=self.blog_article_page), callback=self.parse_blog)

    def parse_html(self, response):
        '''
            随便抓下url
        :param response:
        :return:
        '''
        item = OschinaItem()
        elements = response.css('a::attr(href)')
        all_url = []
        if elements:
            for element in elements:
                _url = element.extract()
                if 'https://www.oschina.net/' in _url:
                    print(_url)
                    # logger.info('随便抓下域名是"www.oschina.net"的url：{}'.format(_url))
                    all_url.append(_url)
                    yield Request(url=_url, callback=self.parse_html)
            logger.info('随便抓下域名是"www.oschina.net"的url')
            item['all_url'] = all_url
            yield item


    def parse_header(self, response):
        '''
            抓取开源中国，首页的项目分类的url
        :param response:
        :return:
        '''
        item = OschinaItem()
        headers = response.css('.nav-item').css('.header > a::attr(href)')
        header_url_list = []  # 开源中国首页的所有项目的url
        if headers:
            for header in headers:
                header_url = header.extract()
                print(header_url)
                logger.info('开源中国的项目url:{}'.format(header_url))
                header_url_list.append(header_url)

                # 递归爬取header_url里的url
                if 'project' in header_url:
                    yield Request(url=header_url,callback=self.parse_project)

                elif 'blog' in header_url:
                    logger.info('准备抓取开源中国博客文章url,抓取的页码为：第{}页'.format(self.blog_article_page))
                    yield Request(url=self.blog_article_base_url.format(page=self.blog_article_page), callback=self.parse_blog)

                # elif 'event' in header_url:
                #     yield Request(url='',callback=)
                #
                # elif 'news' in header_url:
                #     yield Request(url='',callback=)
                #
                # elif 'question' in header_url:
                #     yield Request(url='',callback=)

        item['header_urls'] = header_url_list
        yield item


    def parse_project(self, response):
        '''
            抓取开源中国，软件项目里的所有项目分类的url
        :param response:
        :return:
        '''
        item = OschinaItem()
        project_urls = []  # 软件（project）项目分类的下的所有url
        data = response.css('#v-sort > project-sort').extract_first()
        data = data.strip()
        href_list = re.findall(r"href:'(.*)'", data)
        for href in href_list:
            _url = self.base_url + href
            print(_url)
            logger.info('开源中国软件开源项目类型的url：{}'.format(_url))
            project_urls.append(_url)
            yield Request(url=_url, callback=self.parse_open_source_project)

        item['project_urls'] = project_urls
        yield item


    def parse_open_source_project(self, response):
        '''
            抓取开源中国，软件项目里的所有项目分类里的开源项目的url
        :param response:
        :return:
        '''
        open_source_project_type = ((response.url).split('/')[-1]).split('?')[0]    #开源项目的类型（编程语言）

        item = OschinaItem()
        open_source_project_urls = []  # 软件（project）项目分类的下的所有url
        open_source_projects = response.css('.lists.news-list .item .box-aw > a::attr(href)')
        if open_source_projects:
            for open_source_project in open_source_projects:
                open_source_project_url = open_source_project.extract()
                print(open_source_project_url)
                logger.info('开源中国软件开源项目,开源项目的类型:{type},url:{url}'.format(type=open_source_project_type,url=open_source_project_url))
                open_source_project_urls.append(open_source_project_url)
            item['open_source_project_urls'] = open_source_project_urls
            item['project_type'] = open_source_project_type
            yield item

        # 抓取下一页的url
        open_source_project_url_path = (response.url).split('?')[0]
        pages = response.css('.paging a::text').extract()
        if '下一页' in pages:
            page = (response.css('.paging a::attr(href)').extract())[-1]
            next_page_url = open_source_project_url_path + page
            print('下一页：',next_page_url)
            yield Request(url=next_page_url, callback=self.parse_open_source_project)


    def parse_blog(self, response):
        '''
            抓取开源中国，博客项目里的所有最新文章的url
        :param response:
        :return:
        '''
        item = OschinaItem()
        blog_article_urls = []  # 博客（blog）项目下的所有最新推荐的url

        no_article = response.css('h4::text')  # 有博客文章时为空
        if not no_article == '暂无文章':
            articles = response.css('.header::attr(href)')
            if articles:
                for article in articles:
                    article_url = article.extract()
                    print(article_url)
                    blog_article_urls.append(article_url)
            item['blog_article_urls'] = blog_article_urls
            yield item

            self.blog_article_page += 1
            # print(self.blog_article_page,'-'*100)
            logger.info('准备抓取开源中国博客文章url,抓取的页码为：第{}页'.format(self.blog_article_page))
            yield Request(url=self.blog_article_base_url.format(page=self.blog_article_page), callback=self.parse_blog,
                          dont_filter=True)

        else:
            logging.warning('开源中国博客文章抓取结束,总抓取了{}页'.format(self.blog_article_page))
