# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging

import scrapy
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter, is_item
from playwright.async_api import async_playwright
from scrapy import Request, signals
from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse
from scrapy.exceptions import IgnoreRequest

class PlaywrightMiddleware:
    async def process_request(self, request: scrapy.Request, spider: scrapy.Spider) -> HtmlResponse:
        # Si la requête n'est pas destinée à Playwright, on l'ignore.
        if request.meta.get("playwright_valid_form"):
            async with async_playwright() as p:
                # Lancement avec chromium sans interface graphique
                browser = await p.chromium.launch(headless=True)
                # initialisation d'une nouvelle page
                page = await browser.new_page()

                try:
                    spider.logger.info(f"Accès à {request.url}")
                    # redirection vers l'url
                    await page.goto(request.url
                                    # , timeout=10000
                                   )
                    # Attendre que le bouton soit disponible et cliquer dessus
                    try:
                        # await page.wait_for_selector('//*[@id="user-menu-location"]', timeout=5000)
                        # await page.click('//*[@id="user-menu-location"]')
                        await page.wait_for_selector('//button[@data-modal-toggler-modal-outlet="#geolocation-modal"]', timeout=5000)
                        await page.click('//button[@data-modal-toggler-modal-outlet="#geolocation-modal"]')
                        await page.wait_for_timeout(2000)
                        spider.logger.info("Bouton cliqué")
                        form = await page.query_selector('form#postcode-popup-form')
                        if not form:
                            spider.logger.error("Formulaire introuvable après l'ouverture de la modale")
                        else:
                            spider.logger.info("Formulaire détecté")
                    except Exception as e:
                        spider.logger.error(f"Erreur lors du clic : {e}")

                    # extraction des datas
                    content = await page.content()
                    response = HtmlResponse(
                        url=request.url,
                        body=content,
                        encoding="utf-8",
                        request=request,
                    )
                    return response

                except Exception as error:
                    spider.logger.error(f"Erreur Playwright : {error}")
                    raise IgnoreRequest()

                finally:
                    await browser.close()
        
        elif request.meta.get("playwright_wait_loading_products"):
            async with async_playwright() as p:
                # Lancement avec chromium sans interface graphique
                browser = await p.chromium.launch(headless=True)
                # initialisation d'une nouvelle page
                page = await browser.new_page()
                
                try:
                    spider.logger.info(f"Accès à {request.url}")
                    # redirection vers l'url
                    await page.goto(request.url)
                    await page.wait_for_timeout(2000)
                    
                    content = await page.content()
                    response = HtmlResponse(
                            url=request.url,
                            body=content,
                            encoding="utf-8",
                            request=request,
                        )
                    return response
                    
                    
                                    
                except Exception as error:
                    spider.logger.error(f"Erreur Playwright : {error}")
                    raise IgnoreRequest()
                
        else:
            return None


class ScrapyAppSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider: scrapy.Spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScrapyAppDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider: scrapy.Spider):
        spider.logger.info("Spider opened: %s" % spider.name)
