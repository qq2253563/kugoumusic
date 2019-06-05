# -*- coding: utf-8 -*-
import scrapy

from kugou.items import *
import re
import json
from scrapy.utils.project import get_project_settings
from utils.filter import filter_response
from datetime import datetime


class MusicListSpider(scrapy.Spider):
    name = 'musiclist'
    allowed_domains = ['kugou.com']
    start_urls = ['https://www.kugou.com/yy/html/special.html']

    def parse(self, response):
        images = response.xpath('//li/div[@class="pic"]/a/img/@_src').extract()
        titles = response.xpath('//li/div[@class="pic"]/a/@title').extract()
        names = response.xpath('//li/div[@class="detail"]/div/em/text()').extract()
        urls = response.xpath('//li/div[@class="pic"]/a/@href').extract()
        ids = response.xpath('//ul[@id="ulAlbums"]/li/@class').extract()
        for image, title, name, url, id in zip(images, titles, names, urls, ids):
            item = KugouListItem()
            item['title'] = title
            item['image'] = image
            item['name'] = name
            sid = int(id[2:])
            item['sid'] = sid
            item['type'] = 'kugou_list'
            item['time'] = datetime.now().strftime("%Y-%m-%d")
            yield scrapy.Request(url=url, meta={'id': sid}, callback=self.parse_detail)
            yield item

    def parse_detail(self, response):
        id = response.meta['id']
        music_names = response.xpath('//li/a/@title').extract()
        js_code = response.xpath("//script/text()").extract_first()
        js_re = "[" + re.search(r'\[(.+)\]', js_code).group(1) + "]"
        datas = json.loads(js_re)
        settings = get_project_settings()
        for data, music_name in zip(datas, music_names):
            hashvalue = data['HASH']
            album_id = data['album_id']
            url = "https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQ&hash=" + str(
                hashvalue) + "&album_id=" + str(album_id) + "&dfid=&mid=" + settings.get('KUGOU_MID') + "&platid=4&_="
            music = KugouMusicItem()
            music['sid'] = id
            music['audio_id'] = data['audio_id']
            music['music_name'] = music_name
            yield scrapy.Request(url=url, meta={'music': music}, callback=self.parse_music)

    def parse_music(self, response):
        yield filter_response(response)
