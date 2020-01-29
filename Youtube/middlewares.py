# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import re
import time

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from Youtube.SeleniumRequest import SeleniumRequest


class SeleniumMiddleware:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1200x600')
        options.add_argument("--enable-javascript")
        options.add_argument("--incognito")

        self.driver = webdriver.Chrome("E:\Github\Youtube-Scrapy\chromedriver.exe", chrome_options=options)

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()

        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware

    def process_request(self, request, spider):

        if not isinstance(request, SeleniumRequest):
            return None

        self.driver.get(request.url)

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie(
                {
                    'name': cookie_name,
                    'value': cookie_value
                }
            )

        if request.endless_scrolling:
            html = self.driver.find_element_by_tag_name('html')
            html.send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

            self.driver.execute_script('videos = document.querySelectorAll("video"); for(video of videos) {video.pause(); video.controls = true}')
            self.driver.execute_script('document.getElementById("player").remove();')

            elements = -1
            experimental = -1
            scrolls = 0

            while len(self.driver.find_elements_by_xpath(request.endless_scrolling)) != elements:
                element = self.driver.find_elements_by_xpath(request.endless_scrolling)

                if request.experimental and scrolls >= 3:
                    experimental_element = self.driver.find_elements_by_xpath(request.experimental)

                    if experimental > len(element) / 1.5:
                        break

                    experimental = len(experimental_element)

                print(f"{len(element)}/{elements} [{experimental}]")

                self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                scrolls += 1
                time.sleep(1.6)
                elements = len(element)
            else:
                if request.endless_scrolling == '//*[@id="content-text"]':
                    self.driver.execute_script('buttons = document.getElementsByClassName("more-button-exp style-scope ytd-comment-replies-renderer"); for(button of buttons) {button.click();}');
                    time.sleep(10)

                print("haha")


        body = str.encode(self.driver.page_source)

        request.meta.update({'driver': self.driver})

        return HtmlResponse(
            self.driver.current_url,
            body=body,
            encoding='utf-8',
            request=request
        )

    def spider_closed(self):
        self.driver.quit()

class YoutubeSpiderMiddleware(object):
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

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class YoutubeDownloaderMiddleware(object):
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

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
