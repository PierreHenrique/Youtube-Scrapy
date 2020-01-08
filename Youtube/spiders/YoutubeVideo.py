# -*- coding: utf-8 -*-
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
from Youtube.items import YoutubeVideoItem
import json
import time


class YoutubeVideoSpider(CrawlSpider):
    name = 'YoutubeVideo'
    urls = []

    script1 = """
        function main(splash)
            assert(splash:go(splash.args.url))
            splash.http2_enabled = true
            splash.images_enabled  = false
            splash.html5_media_enabled = false
            splash:wait(splash.args.wait)
            return {html=splash:html()}
        end
        """

    def __init__(self):
        print("Help")
        with open("Youtube.json", "r+") as json_file:
            data = json.load(json_file)
            for url in data[0]['videos']:
                self.urls.append(url)


    def start_requests(self):
        for url in self.urls:
            time.sleep(5)
            print('Sending request')
            yield SplashRequest(url, self.parse, endpoint='execute', args={'har': 1,'html': 1,'lua_source': self.script1,'wait': 2.5, 'timeout': 90}, meta={'original_url': url})

    def parse(self, response):
        video = ItemLoader(item=YoutubeVideoItem(), response=response)

        video.add_value('url', response.meta['original_url'])
        video.add_value('title', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/h1/yt-formatted-string/text()').get())
        video.add_value('views', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/div/div[1]/div[1]/yt-view-count-renderer/span[1]/text()').get())
        video.add_value('likes', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/div/div[3]/div/ytd-menu-renderer/div/ytd-toggle-button-renderer[1]/a/yt-formatted-string/text()').get())
        video.add_value('dislikes', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/div/div[3]/div/ytd-menu-renderer/div/ytd-toggle-button-renderer[2]/a/yt-formatted-string/text()').get())

        yield video.load_item()