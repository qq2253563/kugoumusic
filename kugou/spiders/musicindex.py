# -*- coding: utf-8 -*-
import scrapy
from items import BannerItem, KugouMusicItem, SingleItem
from datetime import datetime
import random
from scrapy.utils.project import get_project_settings
import re
from utils.filter import filter_response
import json


class MusicIndexSpider(scrapy.Spider):
    name = 'musicbanner'
    allowed_domains = ['kugou.com']
    start_urls = ['https://www.kugou.com/']

    def parse(self, response):
        images = response.xpath('//div[@class="banner"]/ul/li/@data-bg').extract()
        urls = response.xpath('//div[@class="banner"]/ul/li/a/@href').extract()
        single_images = response.xpath('//li/div/a[@class="singerLink"]/img/@_src').extract()
        single_urls = response.xpath('//li/div/a[@class="singerLink"]/@href').extract()
        single_names = response.xpath('//li/div/a[@class="singerLink"]/div/p/text()').extract()
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

        for single_url, single_image, single_name in zip(single_urls, single_images, single_names):
            singleItem = SingleItem()
            singleItem['single_id'] = int(single_url.split(".")[2][-4:])
            singleItem['image'] = single_image.replace("/240/", "/480/")
            singleItem['name'] = single_name
            singleItem['type'] = 'kugou_single'
            singleItem['time'] = datetime.now().strftime("%Y-%m-%d")
            yield scrapy.Request(url=single_url, meta={"singleItem": singleItem}, callback=self.parse_singledetail)

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

    def parse_singledetail(self, response):
        singleItem = response.meta['singleItem']
        introduction = response.xpath('//div[@class="intro"]/p/text()').extract()[0]
        singleItem['introduction'] = introduction
        js_code = response.xpath("//script/text()").extract_first()
        js_re = "[" + re.search(r'\[(.+)\]', js_code).group(1) + "]"
        datas = json.loads(js_re)
        settings = get_project_settings()
        for data in datas:
            hashvalue = data['hash']
            album_id = data['album_id']
            url = "https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQ&hash=" + str(
                hashvalue) + "&dfid=&mid=" + settings.get('KUGOU_MID') + "&platid=4&_="
            music = KugouMusicItem()
            music['sid'] = singleItem['single_id']
            music['audio_id'] = album_id
            music['music_name'] = data['audio_name']
            yield scrapy.Request(url=url, meta={'music': music}, callback=self.parse_music)
        yield singleItem
