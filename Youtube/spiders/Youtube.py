# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest

from Youtube.SeleniumRequest import SeleniumRequest
from Youtube.items import YoutubeItem


class YoutubeSpider(CrawlSpider):
    name = 'Youtube'

    def start_requests(self):
        yield SeleniumRequest(url='https://www.youtube.com/user/ElectronicDesireGE/videos', callback=self.parse_item, endless_scrolling='//ytd-grid-video-renderer[@class="style-scope ytd-grid-renderer"]')

    def parse_item(self, response):
        #print(response.body);
        videos = response.xpath('//*[@id="video-title"]/@href').getall()
        youtube = ItemLoader(item=YoutubeItem(), response=response)
        raw_videos = []

        youtube.add_value('author', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/app-header-layout/div/app-header/div[2]/div[2]/div/div[1]/div/div[1]/ytd-channel-name/div/div/yt-formatted-string/text()').get())

        for video in videos:
            if len(video) > 0:
                raw_videos.append(f'https://www.youtube.com{video}')

        if len(raw_videos) > 0:
            youtube.add_value('videos', raw_videos)


        yield youtube.load_item()
