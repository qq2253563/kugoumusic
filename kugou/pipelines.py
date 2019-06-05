# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class BasePipeline(object):
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

    def close_spider(self, spider):
        self.connect.close()


class KugouPipeline(BasePipeline):

    def process_item(self, item, spider):
        typeclass = item['type']
        if typeclass == 'kugou_list':
            self.cursor.execute("""select * from music_list where id = %s""", item["sid"])
            ret = self.cursor.fetchone()
            if ret:
                self.cursor.execute(
                    """update music_list set title = %s, image=%s, name=%s, bg_time=%s, type=1 where id=%s """,
                    (item['title'], item['image'], item['name'], item['time'], item['sid']))
            else:
                self.cursor.execute(
                    """insert into music_list (title, image, name, id, bg_time, type) value (%s, %s, %s, %s, %s, 1)""",
                    (item['title'], item['image'], item['name'], item['sid'], item['time']))  # item里面定义的字段和表字段对应
            # 提交sql语句
            self.connect.commit()
            return item
        elif typeclass == 'kugou_music':
            self.cursor.execute("""select * from music_detail where id = %s""", item["audio_id"])
            ret = self.cursor.fetchone()
            if ret:
                self.cursor.execute(
                    """update music_detail set name=%s, content=%s, bg_time=%s, sid=%s, type = 1 where id=%s """,
                    # 纯属python操作mysql知识，不熟悉请恶补
                    (item['music_name'],
                     item['music_data'],
                     item['time'],
                     item['sid'],
                     item['audio_id']))  # item里面定义的字段和表字段对应
            else:
                self.cursor.execute(
                    """insert into music_detail(name, content, bg_time, sid, id, type)
                    value (%s, %s, %s, %s, %s, 1)""",  # 纯属python操作mysql知识，不熟悉请恶补
                    (item['music_name'],
                     item['music_data'],
                     item['time'],
                     item['sid'],
                     item['audio_id']))  # item里面定义的字段和表字段对应
            # 提交sql语句
            self.connect.commit()
            return item
        else:
            return item


class IndexPipeline(BasePipeline):
    def process_item(self, item, spider):
        typeclass = item['type']
        if typeclass == 'kugou_banner':
            self.cursor.execute(
                """insert into music_banner (id, image, bg_time, url, type) value (%s, %s, %s, %s, 1)""",
                (item['banner_id'], item['image'], item['url'], item['time']))  # item里面定义的字段和表字段对应
            # 提交sql语句
            self.connect.commit()
        return item