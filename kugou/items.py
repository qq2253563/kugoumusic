# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.org/en/latest/topics/items.html

from scrapy import Item, Field


class KugouListItem(Item):
    type = Field()
    sid = Field()
    name = Field()
    title = Field()
    image = Field()
    content = Field()
    time = Field()


class KugouMusicItem(Item):
    type = Field()
    audio_id = Field()
    music_name = Field()
    sid = Field()
    music_data = Field()
    time = Field()


class BannerItem(Item):
    banner_id = Field()
    type = Field()
    image = Field()
    time = Field()
    url = Field()
