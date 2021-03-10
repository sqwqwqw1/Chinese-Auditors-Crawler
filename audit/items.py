# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FirmItem(scrapy.Item):
    _id = scrapy.Field()


class NwperItem(scrapy.Item):
    _id = scrapy.Field()

class CpaItem(scrapy.Item):
    _id = scrapy.Field()

class ProfileItem(scrapy.Item):
    _id = scrapy.Field()