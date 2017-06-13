# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FoursquareItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    deep = scrapy.Field()
    contact = scrapy.Field()
    followers = scrapy.Field()
    following = scrapy.Field()
    position_tips = scrapy.Field()
