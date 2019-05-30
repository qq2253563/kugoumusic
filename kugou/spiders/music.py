# -*- coding: utf-8 -*-
import scrapy

from kugou.items import KugouItem, MusicItem
import re
import json
import time


class MusicSpider(scrapy.Spider):
    name = 'music'
    allowed_domains = ['kugou.com']
    start_urls = ['https://www.kugou.com/yy/html/special.html']

    def parse(self, response):
        images = response.xpath('//li/div[@class="pic"]/a/img/@_src').extract()
        titles = response.xpath('//li/div[@class="pic"]/a/@title').extract()
        contents = response.xpath('//li/div[@class="detail"]/div[@class="text"]/text()').extract()
        urls = response.xpath('//li/div[@class="pic"]/a/@href').extract()
        ids = response.xpath('//ul[@id="ulAlbums"]/li/@class').extract()
        for image, title, content, url, id in zip(images, titles, contents, urls, ids):
            item = KugouItem()
            item['title'] = title
            item['image'] = image
            item['content'] = content
            sid = int(id[2:])
            item['sid'] = sid
            # scrapy.Request(url=url, meta={'id': sid}, callback=self.parse_detail)
            yield item

    def parse_detail(self, response):
        id = response.meta['id']
        music_names = response.xpath('//li/a/@title').extract()
        js_code = response.xpath("//script/text()").extract_first()
        js_re = "[" + re.search(r'\[(.+)\]', js_code).group(1) + "]"
        datas = json.loads(js_re)
        for data, music_name in zip(datas, music_names):
            hashvalue = data['HASH']
            album_id = data['album_id']
            url = "https://wwwapi.kugou.com/yy/index.php?r=play/getdata&callback=jQ&hash=" + str(
                hashvalue) + "&album_id=" + str(album_id) + "&dfid=&mid=2db3c8077a7647f44e4ed12003557285&platid=4&_="
            music = MusicItem()
            music['sid'] = id
            music['album_id'] = album_id
            music['music_name'] = music_name
            yield scrapy.Request(url=url, meta={'music': music}, callback=self.parse_music)

    def parse_music(self, response):
        music = response.meta['music']
        re_json = response.text[3:-2]
        music['music_data'] = re_json
        music['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        yield music
