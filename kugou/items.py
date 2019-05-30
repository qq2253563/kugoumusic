# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class KugouItem(scrapy.Item):
    sid = scrapy.Field()
    name = scrapy.Field()
    title = scrapy.Field()
    image = scrapy.Field()
    content = scrapy.Field()
    __class__ = 'kugou.items.KugouItem'


class MusicItem(scrapy.Item):
    album_id = scrapy.Field()
    music_name = scrapy.Field()
    sid = scrapy.Field()
    music_data = scrapy.Field()
    time = scrapy.Field()
    __class__ = 'kugou.items.MusicItem'