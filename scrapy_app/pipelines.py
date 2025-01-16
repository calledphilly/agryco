# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import re
from unicodedata import category

import scrapy
import scrapy.exceptions
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from networkx import scale_free_graph
from numpy import empty

from scrapy_app.items import CategoryItem, ProductItem, SubCategoryItem
# from scrapy_app.models import CategoryModele, Session, SubCategoryModele
from scrapy_app.spiders.categories_spiders import (CategorySpider, SubCategorySpider)
from scrapy_app.spiders.products_spiders import ProductSpider

# class ScrapyAppPipeline:

#     def process_item(self, item, spider):
#         return item


class DuplicatesItemPipeline:

    def __init__(self):
        self.seen_names = set()

    def process_item(self, item: SubCategoryItem | CategoryItem | ProductItem,
                     spider: CategorySpider | SubCategorySpider | ProductSpider) -> SubCategoryItem | CategoryItem | ProductItem:
        if not item['name']:
            raise scrapy.exceptions.DropItem(f"Name field is empty : '{item['name']}'")

        if item['name'] in self.seen_names:
            raise scrapy.exceptions.DropItem(f"'{item['name']}' is already exist")

        self.seen_names.add(item['name'])

        return item


class DefaultFieldPipeline:

    def process_item(self, item: SubCategoryItem | CategoryItem,
                     spide: CategorySpider | SubCategorySpider) -> SubCategoryItem | CategoryItem:
        if isinstance(item, CategoryItem):
            item['state'] = 'category'

        if isinstance(item, SubCategoryItem):
            item['state'] = 'sub_category'

        return item


class WashItemPipeline:
    def process_item(self, item: SubCategoryItem | CategoryItem | ProductItem,
                     spider: CategorySpider | SubCategorySpider | ProductSpider) -> SubCategoryItem | CategoryItem | ProductItem:
        if isinstance(item, SubCategoryItem) or isinstance(item, CategoryItem):
            item['name'] = item['name'].replace("(", "").replace(")", "")
            item['name'] = re.sub(r'\d+', '', item['name'])
            item['name'] = item['name'].strip()
            return item
        elif isinstance(item, ProductItem):
            if item['price'] is not ".":
                item['price'] = item['price'].replace("€","").replace(" ","").replace(" ","")
            else:
                item['price'] = ""
            return item


# class PostgresqlPipeline:
#     def __init__(self):
#         self.session = None

#     def process_item(self, item: SubCategoryItem | CategoryItem, spider: CategorySpider | SubCategorySpider ) -> CategoryItem | SubCategoryItem:
#         self.session = Session()
#         if item['state'] == 'category':
#             db_category = self.session.query(CategoryModele).filter_by(name=item['name']).first()
#             if not db_category:
#                 db_category = CategoryModele(
#                     name = item['name'],
#                     url = item['url'],
#                     state = item['state']
#                 )

#                 self.session.add(db_category)
#                 self.session.commit()
#             else:
#                 logging.error(f'{item} already exits in {CategoryModele()}')

#         elif item['state'] == 'sub_category':
#             db_sub_category = self.session.query(SubCategoryModele).filter_by(name=item['name']).first()
#             if not db_sub_category:
#                 db_category: CategoryModele = self.session.query(CategoryModele).filter_by(url=item['super_category_url']).first()
#                 if db_category:
#                     db_sub_category = SubCategoryModele(
#                         name = item['name'],
#                         url = item['url'],
#                         state = item['state'],
#                         id_super_category = db_category.id
#                     )

#                     self.session.add(db_sub_category)
#                     self.session.commit()
#                 else:
#                     logging.error(f"Category with {item['super_category_url']} not found in {CategoryModele()}")
#             else:
#                 logging.error(f'{item['name']} already exits in {SubCategoryModele()}')
#         self.session.close()
#         return item
