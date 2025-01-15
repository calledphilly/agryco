import scrapy
from scrapy.http import HtmlResponse

from scrapy_app.items import CategoryItem, SubCategoryItem, ProductItem
class PriceSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["www.agryco.com"]
    start_urls = ["https://www.agryco.com"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, meta={"playwright": True})

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
            yield response.follow(url, self.parse_category)

    def parse_category(self, response: HtmlResponse):
        nav = response.xpath('//li[contains(@class, "nav-item   nav-parent-item")]//li[contains(@class, "nav-item ")]')
        for category in nav:
            item = CategoryItem()
            item["url"] = category.xpath('./a[@class="nav-link"]/@href').get(default='')
            yield response.follow(item['url'], self.parse_sub_category, cb_kwargs={'super_category_url': item['url']})

        item = CategoryItem()
        item['url'] = response.xpath('//li[@id="menu-13"]/a/@href').get(default='')
        yield response.follow(item['url'], self.parse_sub_category, cb_kwargs={'super_category_url': item['url']})

    def parse_sub_category(self, response: HtmlResponse, super_category_url: str):
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

        def follow_sub_categories(xpath_base: str, xpath_for_get_url: str, xpath_for_get_name: str):
            for sub_category in response.xpath(xpath_base):
                item = SubCategoryItem()
                item['url'] = sub_category.xpath(xpath_for_get_url).get(default='').strip()
                item['name'] = sub_category.xpath(xpath_for_get_name).get(default='').strip()
                item['super_category_url'] = super_category_url
                yield response.follow(item['url'], self.parse_product)

        for key in xpath_sub_categories:
            yield from follow_sub_categories(xpath_sub_categories[key]['base'], xpath_sub_categories[key]['url'],
                                             xpath_sub_categories[key]['name'])

    def parse_product(self, response: HtmlResponse):
        products = response.xpath('//div[@class="product-teaser __gtm-parsed"]').getall()
        for product in products:
            product = ProductItem()
            product['name'] = product.xpath('.//div[@class="content"]/div[@class="description-product"]/div[@class="information"]/h2/a[@class="product-name stretched-link"]/text()').get(default='').strip()
            product['price'] = product.xpath('.//div[@class="base-price"]/div[@class="amout"]/span/slot[@name="int"]/text()').get(default='').strip()
            product['price'] += ","
            product['price'] = product.xpath('.//div[@class="base-price"]/div[@class="amout"]/span/span/slot[@name="dec"]/text()').get(default='').strip()
            yield product