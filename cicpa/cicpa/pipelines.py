# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo


class CicpaPipeline:
    def __init__(self):
        client = pymongo.MongoClient('mongodb://localhost:27017')
        database = client['cicpa']
        self.collection = database['cpa']

    def process_item(self, item, spider):
        self.collection.insert_one(item)
        return item
