from typing import Any
from bs4 import BeautifulSoup
import scrapy
from scrapy.http import HtmlResponse

from scrapy_app.items import CategoryItem, ProductItem, SubCategoryItem


class ProductSpider(scrapy.Spider):        
    name = "product"
    allowed_domains = ["www.agryco.com"]
    start_urls = ["https://www.agryco.com"]
    products_urls = set()

    def parse(self, response: HtmlResponse):
        nav = response.xpath('//li[contains(@class, "nav-item   nav-parent-item")]//li[contains(@class, "nav-item ")]')
        for category in nav:
            item = CategoryItem()
            item["url"] = category.xpath('./a[@class="nav-link"]/@href').get(default='')
            yield response.follow(item['url'], self.follow_sub_category, cb_kwargs={'super_category_url': item['url']})

        item = CategoryItem()
        item['url'] = response.xpath('//li[@id="menu-13"]/a/@href').get(default='')
        yield response.follow(item['url'], self.follow_sub_category, cb_kwargs={'super_category_url': item['url']})

    def follow_sub_category(self, response: HtmlResponse, super_category_url: str):
        xpath_sub_categories = {
            'type_1': {
                'base': '//div[@class="liste_sousCat"]/ul/li',
                'url': './a/@href',
                'name': './a/text()',
            },
            'type_2_1': {
                'base': '//div[@class="rangerw "]/ul/li',
                'url': './/a/@href',
                'name': './/div[@class="rangedt"]/h3/text()',
            },
            'type_2_2': {
                'base': '//ul[@class="splide__list"]/li[contains(@class, "splide__slide")]',
                'url': './/a/@href',
                'name': './/div[@class="rangedt"]/h3/text()',
            },
            'type_2_3': {
                'base': '//ul[@class="splide__list"]/li[contains(@class, "splide__slide")]',
                'url': './/a/@href',
                'name': './/div[@class="rangedt"]/h4/text()',
            },
            'type_3': {
                'base': '//div[@class="category-list"]/ul/li',
                'url': './a/@href',
                'name': 'normalize-space(./a)',
            },
            'type_4': {
                'base': '//div[contains(@class, "bloc-categorie ")]/ul/li',
                'url': './a/@href',
                'name': 'normalize-space(./a)',
            },
            'type_5': {
                'base': '//ul[contains(@class, "sub-filters")]/li',
                'url': './/a[@class="sub-category-name"]/@href',
                'name': 'normalize-space(.//a[@class="sub-category-name"]/text())',
            },
        }

        def follow_url(xpath_base: str, xpath_for_get_url: str, xpath_for_get_name: str):
            for sub_category in response.xpath(xpath_base):
                item = SubCategoryItem()
                item['url'] = sub_category.xpath(xpath_for_get_url).get(default='').strip()
                item['name'] = sub_category.xpath(xpath_for_get_name).get(default='').strip()
                item['super_category_url'] = super_category_url
                yield response.follow(url=item['url'], callback=self.follow_product, meta={"playwright_wait_loading_product": True})

        for key in xpath_sub_categories:
            yield from follow_url(xpath_sub_categories[key]['base'], xpath_sub_categories[key]['url'],
                                             xpath_sub_categories[key]['name'])

    def follow_product(self, response: HtmlResponse):
        products_urls = response.xpath('//a[@class="product-name stretched-link"]/@href').getall()
        for product_url in products_urls:
            self.products_urls.add(product_url)
            yield response.follow(url=product_url, callback=self.valid_form, meta={"playwright_valid_form": True })
    
    def valid_form(self, response: HtmlResponse):
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                'town_email[town][_postcode]': '92000',
                'town_email[town][_select_town]': '36467',
                'town_email[email]': 'gallery-kosher-9o@icloud.com',
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

        # Continuer à scraper des pages protégées
        for url in self.products_urls:
            yield response.follow(url, self.parse_product, meta={"playwright_wait_loading_products": True })
            
    def parse_product(self, response: HtmlResponse):
        item = ProductItem()
        item['name'] = response.xpath('//h1[@class="product-title"]/text()').get(default='').strip()
        item['url'] = response.url
        item['description'] = response.xpath('//div[@class="product-detail"]/p/text()').get(default='').strip()
        item['price'] = response.xpath('//p[@class="block-price"]/span[@class="price"]/text()').get(default='').strip()
        item['price'] += "."
        item['price'] += response.xpath('//p[@class="block-price"]/span[@class="price"]/span[@class="decimal"]/text()').get(default='').strip()
        yield item

class SS(scrapy.Spider):
    name = "ss"
    allowed_domains = ["www.agryco.com"]
    start_urls = ["https://www.agryco.com/soc-de-cultivateur-reversible-75-x-12-20-ea75/p199142"]
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, meta={"playwright_valid_form": True })
    
    def parse(self, response: HtmlResponse):
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                'town_email[town][_postcode]': '92000',
                'town_email[town][_select_town]': '36467',
                'town_email[email]': 'gallery-kosher-9o@icloud.com',
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

        # Continuer à scraper des pages protégées
        for url in self.start_urls:
            self.logger.info("authentificatin validé")
            yield response.follow(url, self.parse_product, meta={"playwright_wait_loading_products": True })
    
    def parse_product(self, response: HtmlResponse):
        soup = BeautifulSoup(response.body, 'html.parser')
        formatted_html = soup.prettify()
        # Loguer le HTML formaté
        self.logger.info(f"Formatted HTML Body:\n{formatted_html}") 
        item = ProductItem()
        item['name'] = response.xpath('//h1[@class="product-title"]/text()').get(default='').strip()
        item['url'] = response.url
        item['description'] = response.xpath('//div[@class="product-detail"]/p/text()').get(default='').strip()
        item['price'] = response.xpath('//p[@class="block-price"]/span[@class="price"]/text()').get(default='').strip()
        item['price'] += "."
        item['price'] += response.xpath('//p[@class="block-price"]/span[@class="price"]/span[@class="decimal"]/text()').get(default='').strip()
        yield item