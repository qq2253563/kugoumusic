# -*- coding: utf-8 -*-
import scrapy
from items import BannerItem, KugouMusicItem
from datetime import datetime
import random
from scrapy.utils.project import get_project_settings
from utils.filter import filter_response


class MusicBannerSpider(scrapy.Spider):

    name = 'musicbanner'
    allowed_domains = ['kugou.com']
    start_urls = ['https://www.kugou.com/']

    def parse(self, response):
        images = response.xpath('//div[@class="banner"]/ul/li/@data-bg').extract()
        urls = response.xpath('//div[@class="banner"]/ul/li/a/@href').extract()
        rid = random.randint(1, 100)
        for image, url in zip(images, urls):
            bannerItem = BannerItem()
            bannerItem['banner_id'] = rid
            bannerItem['image'] = image
            bannerItem['type'] = 'kugou_banner'
            bannerItem['time'] = datetime.now().strftime("%Y-%m-%d")
            bannerItem['url'] = url
            rid += 1
            if url.find('single') > 0:
                bannerItem['banner_id'] = url.split("=")[1]
                id = bannerItem['banner_id']
                bannerItem['url'] = ''
                yield scrapy.Request(url=url, meta={"id": int(id)}, callback=self.parse_detail)
            yield bannerItem

    def parse_detail(self, response):
        id = response.meta['id']
        music_names = response.xpath('//li/a/@title').extract()
        music_hashs = response.xpath('//li/a/@data').extract()
        settings = get_project_settings()
        for music_hash, music_name in zip(music_hashs, music_names):
            music_hash_list = music_hash.split("|")
            hashvalue = music_hash_list[0]
            album_id = music_hash_list[1]
            url = "https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQ&hash=" + str(
                hashvalue) + "&dfid=&mid=" + settings.get('KUGOU_MID') + "&platid=4&_="
            music = KugouMusicItem()
            music['sid'] = id
            music['audio_id'] = album_id
            music['music_name'] = music_name
            yield scrapy.Request(url=url, meta={'music': music}, callback=self.parse_music)

    def parse_music(self, response):
        yield filter_response(response)

