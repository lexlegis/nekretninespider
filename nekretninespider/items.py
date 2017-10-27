# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NekretninespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AdItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    location = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()
    rating = scrapy.Field()
    updated = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()
    file_paths = scrapy.Field()
