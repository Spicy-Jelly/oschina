# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class OschinaItem(scrapy.Item):
    # define the fields for your item here like:
    all_url = scrapy.Field()
    header_urls = scrapy.Field()
    project_urls = scrapy.Field()
    project_type = scrapy.Field()
    open_source_project_urls = scrapy.Field()
    blog_article_urls = scrapy.Field()
