# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from items import KugouItem, MusicItem
import pymysql


class KugouPipeline(object):
    table_name = 'kugou'

    def __init__(self, mysql_uri, mysql_db, mysql_user, mysql_password):
        self.mysql_uri = mysql_uri
        self.mysql_db = mysql_db
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_uri=crawler.settings.get('MYSQL_URI'),
            mysql_db=crawler.settings.get('MONGO_DATABASE', 'myproject'),
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_password=crawler.settings.get('MYSQL_PASSWORD')
        )

    def open_spider(self, spider):
        self.connect = pymysql.connect(
            host=self.mysql_uri,
            db=self.mysql_db,
            port=3306,
            user=self.mysql_user,
            passwd=self.mysql_password,
            charset='utf8',
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        if issubclass(item, KugouItem):
            self.cursor.execute("""select * from kugou where kg_id = %d""", item["sid"])
            ret = self.cursor.fetchone()
            if ret:
                self.cursor.execute(
                    """update kugou set title = %s, image=%s, content=%s where kg_id=%d """,  # 纯属python操作mysql知识，不熟悉请恶补
                    (item['title'],
                     item['image'],
                     item['content'],
                     item['sid']))  # item里面定义的字段和表字段对应
            else:
                self.cursor.execute(
                    """insert into kugou(title, image, content ,kg_id)
                    value (%s, %s, %s, %d)""",  # 纯属python操作mysql知识，不熟悉请恶补
                    (item['title'],
                     item['image'],
                     item['content'],
                     item['sid']))  # item里面定义的字段和表字段对应
            # 提交sql语句
            self.connect.commit()
            return item
        elif item.__class__ == MusicItem:
            self.cursor.execute("""select * from kugou where kg_id = %d""", item["album_id"])
            ret = self.cursor.fetchone()
            if ret:
                self.cursor.execute(
                    """update kugou set name=%s, content=%s, time=%s,search_id=%d, where kg_id=%d """,
                    # 纯属python操作mysql知识，不熟悉请恶补
                    (item['music_name'],
                     item['music_data'],
                     item['time'],
                     item['sid'],
                     item['album_id']))  # item里面定义的字段和表字段对应
            else:
                self.cursor.execute(
                    """insert into kugou(name, content, time, search_id, kg_id)
                    value (%s, %s, %s, %d, %d)""",  # 纯属python操作mysql知识，不熟悉请恶补
                    (item['music_name'],
                     item['music_data'],
                     item['time'],
                     item['sid'],
                     item['album_id']))  # item里面定义的字段和表字段对应
            # 提交sql语句
            self.connect.commit()
            return item
        else:
            return item

    def close_spider(self, spider):
        self.connect.close()
