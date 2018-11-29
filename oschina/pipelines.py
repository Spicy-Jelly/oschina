# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class OschinaPipeline(object):
# def process_item(self, item, spider):
#         return item

import redis


class RedisPipeline(object):
    '''
        所有的url都用集合sadd存储，避免存在重复的url
    '''

    def __init__(self, redis_host, redis_port, redis_db):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            redis_host=crawler.settings.get('REDIS_HOST'),
            redis_port=crawler.settings.get('REDIS_PORT'),
            redis_db=crawler.settings.get('REDIS_DB')
        )

    def open_spider(self, spider):
        # print('open_spider:连接redis','-'*100)
        self.client = redis.StrictRedis(self.redis_host, self.redis_port, self.redis_db)

    def close_spider(self, spider):
        # print('close_spider','-'*100)
        pass

    def process_item(self, item, spider):
        if item.get('all_url'):
            print('all_url : 操作redis', '-' * 100)
            r = self.client
            for _url in item['all_url']:
                _key = 'oschina:all_url'
                r.sadd(_key, _url)

        if item.get('header_urls'):
            print('header_urls : 操作redis', '-' * 100)
            r = self.client
            for _url in item['header_urls']:
                _key = 'oschina:header_urls'
                r.sadd(_key, _url)

        if item.get('project_urls'):
            print('project_urls : 操作redis', '-' * 100)
            r = self.client
            for _url in item['project_urls']:
                _key = 'oschina:project:project_urls'
                r.sadd(_key, _url)

        if item.get('open_source_project_urls') and item.get('project_type'):
            print('open_source_project_urls : 操作redis', '-' * 100)
            project_type = item['project_type']
            r = self.client
            for _url in item['open_source_project_urls']:
                _key = 'oschina:project:' + str(project_type) + ':open_source_project_urls'
                r.sadd(_key, _url)

        if item.get('blog_article_urls'):
            print('blog_article_urls : 操作redis', '-' * 100)
            r = self.client
            for _url in item['blog_article_urls']:
                _key = 'oschina:blog:blog_article_urls'
                r.sadd(_key, _url)

        return item