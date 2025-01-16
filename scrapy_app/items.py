# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from typing import Any, NoReturn

import scrapy

# class ScrapyAppItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass


class CategoryItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    state = scrapy.Field()


class SubCategoryItem(CategoryItem):
    super_category_url = scrapy.Field()
    pass

class ProductItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    price = scrapy.Field()
