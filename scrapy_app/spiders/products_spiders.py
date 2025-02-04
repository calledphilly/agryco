import os
from collections.abc import Iterable

import scrapy
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from scrapy.http import HtmlResponse

from scrapy_app.items import ProductItem
from scrapy_app.models import Session, SubCategoryModel

# Charge le fichier .env
load_dotenv()
# Accède aux variables d'environnement
EMAIL = os.getenv('EMAIL')


class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["www.agryco.com"]
    start_urls = ["https://www.agryco.com"]

    session = Session()
    sub_categories = session.query(SubCategoryModel).all()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, meta={"playwright_valid_form": True})

    def parse(self, response: HtmlResponse):
        yield scrapy.FormRequest.from_response(
            response,
            formdata={
                'town_email[town][_postcode]': '92000',
                'town_email[town][_select_town]': '36467',
                'town_email[email]': EMAIL,
                '_redirect': response.xpath('//input[@name="_redirect"]/@value').get(),
            },
            formxpath='//form[@id="postcode-popup-form"]',
            callback=self.after_login,
        )

    def after_login(self, response: HtmlResponse):
        # Vérifiez si la connexion a réussi
        if "identifiants incorrects" in response.text.lower():
            self.logger.error("Échec de la connexion")
            return

        for sub_category in self.sub_categories:
            # self.logger.info(f'url : {sub_category.url}')
            yield response.follow(sub_category.url, self.follow_product, meta={"playwright_wait_loading_products": True})

    def follow_product(self, response: HtmlResponse):
        products_urls = response.xpath('//a[@class="product-name stretched-link"]/@href').getall()
        for product_url in products_urls:
            yield response.follow(url=product_url,
                                  callback=self.parse_product,
                                  meta={"playwright_wait_loading_products": True},
                                  cb_kwargs={'sub_category_url': response.url})

    def parse_product(self, response: HtmlResponse, sub_category_url: str):
        soup = BeautifulSoup(response.body, 'html.parser')
        p_tag = soup.find('p', class_="block-price")

        if p_tag:
            formatted_html = p_tag.prettify()
            # Loguer le HTML formaté
            self.logger.info(f"Formatted HTML Body:\n\n{formatted_html}")

        else:
            self.logger.info('Tag not found\n\n')

        cookies = response.headers.getlist('Set-Cookie')
        print(cookies)

        item = ProductItem()
        item['name'] = response.xpath('//h1[@class="product-title"]/text()').get(default='').strip()
        item['url'] = response.url
        item['description'] = response.xpath('//div[@class="product-detail"]/p/text()').get(default='').strip()

        item['super_category_url'] = sub_category_url

        item['price'] = response.xpath('//p[@class="block-price"]/span[@class="price"]/text()').get(default='').strip()
        item['price'] += "."
        item['price'] += response.xpath('//p[@class="block-price"]/span[@class="price"]/span[@class="decimal"]/text()').get(
            default='').strip()
        yield item


class SsSpider(scrapy.Spider):
    name = "ss"
    allowed_domains = ["www.agryco.com"]
    start_urls = [
        "https://www.agryco.com/ibc-de-melasse-de-canne-a-sucre/p456718",
    ]
    session = Session()
    sub_categories = session.query(SubCategoryModel).all()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, meta={"playwright_valid_form": True})

    def parse(self, response: HtmlResponse):
        fetch_city_name = response.xpath('//input[@id="town_email_town__postcode"]').get()
        self.logger.info(f'fetch_city_name : {fetch_city_name}\n\n\n')
        # yield scrapy.FormRequest.from_response(
        #     response,
        #     formdata={
        #         'town_email[town][_postcode]': '93000',
        #         # 'town_email[town][_select_town]': '36467', # Nanterre
        #         'town_email[town][_select_town]': fetch_city_name,
        #         'town_email[email]': EMAIL,
        #         '_redirect': response.xpath('//input[@name="_redirect"]/@value').get(),
        #     },
        #     formxpath='//form[@id="postcode-popup-form"]',
        #     callback=self.after_login,
        # )

    def after_login(self, response: HtmlResponse):
        # Vérifiez si la connexion a réussi
        if "identifiants incorrects" in response.text.lower():
            self.logger.error("Échec de la connexion")
            return

        yield response.follow(response.url, self.parse_product, meta={"playwright_wait_loading_products": True, "timeout" : 30000})

    def parse_product(self, response: HtmlResponse):
        soup = BeautifulSoup(response.body, 'html.parser')
        div_tag = soup.find('div', class_="block-offer")

        if div_tag:
            formatted_html = div_tag.prettify()
            # Loguer le HTML formaté
            self.logger.info(f"Formatted HTML:\n\n{formatted_html}\n\n")

        else:
            self.logger.info('Tag not found\n\n')

        item = ProductItem()
        item['name'] = response.xpath('//h1[@class="product-title"]/text()').get(default='').strip()
        item['url'] = response.url
        item['description'] = response.xpath('//div[@class="product-detail"]/p/text()').get(default='').strip()

        # item['super_category_url'] = sub_category_url

        item['price'] = response.xpath('//p[@class="block-price"]/span[@class="price"]/text()').get(default='').strip()
        if item['price']:
            item['price'] += "."
            item['price'] += response.xpath('//p[@class="block-price"]/span[@class="price"]/span[@class="decimal"]/text()').get(
                default='').strip()
        else:
            self.logger.info('item is empty')
            item['price'] = response.xpath('//p[@class="block-price"]/span[@class="price"]/@content').get(default='').strip()
            pass
        yield item
