# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import re

import scrapy
import scrapy.exceptions
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from networkx import scale_free_graph
from numpy import empty

from scrapy_app.items import CategoryItem, ProductItem, SubCategoryItem
from scrapy_app.models import CategoryModel, ProductModel, Session, SubCategoryModel
from scrapy_app.spiders.categories_spiders import (CategorySpider,
                                                   SubCategorySpider)
from scrapy_app.spiders.products_spiders import ProductSpider

# class ScrapyAppPipeline:

#     def process_item(self, item, spider):
#         return item


class DuplicatesItemPipeline:

    def __init__(self):
        self.seen_names = set()

    def process_item(self, item: SubCategoryItem | CategoryItem | ProductItem, spider) -> SubCategoryItem | CategoryItem | ProductItem:
        if not item['name']:
            raise scrapy.exceptions.DropItem(f"Name field is empty : '{item['name']}'")

        if item['name'] in self.seen_names:
            raise scrapy.exceptions.DropItem(f"'{item['name']}' is already exist")

        self.seen_names.add(item['name'])

        return item


class DefaultFieldPipeline:

    def process_item(self, item: SubCategoryItem | CategoryItem, spide) -> SubCategoryItem | CategoryItem:
        if isinstance(item, CategoryItem) and not isinstance(item, SubCategoryItem) :
            item['state'] = 'category'

        elif isinstance(item, SubCategoryItem):
            item['state'] = 'sub_category'

        return item


class WashItemPipeline:
    def process_item(self, item: SubCategoryItem | CategoryItem | ProductItem, spider) -> SubCategoryItem | CategoryItem | ProductItem:
        if isinstance(item, CategoryItem):
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


class PostgresqlPipeline:
    def __init__(self):
        self.session = None

    def process_item(self, item: SubCategoryItem | CategoryItem | ProductItem,
                     spider: CategorySpider | SubCategorySpider | ProductSpider ) -> CategoryItem | SubCategoryItem | ProductItem:
        self.session = Session()
        if isinstance(item, CategoryItem) and not isinstance(item, SubCategoryItem):
            category = self.session.query(CategoryModel).filter_by(name=item['name']).first()
            if not category:
                category = CategoryModel(
                    name = item['name'],
                    url = item['url'],
                )

                self.session.add(category)
                self.session.commit()
            else:
                spider.logger.error(f'{item} already exits in {CategoryModel()}')

        elif isinstance(item, SubCategoryItem):
            sub_category = self.session.query(SubCategoryModel).filter_by(name=item['name']).first()
            if not sub_category:
                category: CategoryModel = self.session.query(CategoryModel).filter_by(url=item['super_category_url']).first()
                if category:
                    sub_category = SubCategoryModel(
                        name = item['name'],
                        url = item['url'],
                        id_category = category.id
                    )

                    self.session.add(sub_category)
                    self.session.commit()
                else:
                    spider.logger.error(f"Category with {item['super_category_url']} not found in {CategoryModel()}")
            else:
                spider.logger.error(f'{item['name']} already exits in {SubCategoryModel()}')
            
        elif isinstance(item, ProductItem):
            product = self.session.query(ProductModel).filter_by(name=item['name']).first()
            if not product:
                sub_category: SubCategoryModel = self.session.query(SubCategoryModel).filter_by(url=item['super_category_url']).first()
                if sub_category:
                    product = ProductModel(
                        name = item['name'],
                        url = item['url'],
                        description = item['description'],
                        price = item['price'],
                        id_sub_category = sub_category.id,
                    )
                    
                    self.session.add(product)
                    self.session.commit()
                else:
                    spider.logger.error(f"SubCategory with {item['super_category_url']} not found in {SubCategoryModel()}")
            else:
                spider.logger.error(f'{item['name']} already exits in {ProductModel()}')

        self.session.close()
        return item
