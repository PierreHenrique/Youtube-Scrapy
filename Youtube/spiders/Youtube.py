# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider

from Youtube.SeleniumRequest import SeleniumRequest
from Youtube.items import YoutubeItem


class YoutubeSpider(CrawlSpider):
    name = 'Youtube'
    urls = ['https://www.youtube.com/channel/UCYbK_tjZ2OrIZFBvU6CCMiA']

    def start_requests(self):
        for url in self.urls:
            yield SeleniumRequest(url=url, callback=self.parse_featured)

    def parse_featured(self, response):
        subscribers = response.xpath('//yt-formatted-string[@id="subscriber-count"]/text()').get()
        partners = response.xpath('//ytd-mini-channel-renderer/a[@id="channel-info"]/@href').getall()

        yield SeleniumRequest(url=f'{response.request.url}/videos', callback=self.parse_videos, endless_scrolling='//ytd-grid-video-renderer[@class="style-scope ytd-grid-renderer"]', meta={'subscribers': subscribers, 'partners': partners})

    def parse_videos(self, response):
        videos = response.xpath('//*[@id="video-title"]/@href').getall()
        youtube = ItemLoader(item=YoutubeItem(), response=response)
        raw_videos = []

        is_verified = response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/app-header-layout/div/app-header/div[2]/div[2]/div/div[1]/div/div[1]/ytd-channel-name/ytd-badge-supported-renderer/div/paper-tooltip/div/text()').get()

        if is_verified is not None and len(is_verified) > 0:
            is_verified = 'true'
        else:
            is_verified = 'false'

        youtube.add_value('id', response.request.url)
        youtube.add_value('name', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/app-header-layout/div/app-header/div[2]/div[2]/div/div[1]/div/div[1]/ytd-channel-name/div/div/yt-formatted-string/text()').get())
        youtube.add_value('partners', response.meta["partners"])
        youtube.add_value('subscribers', response.meta["subscribers"])
        youtube.add_value('is_verified', is_verified)

        for video in videos:
            if len(video) > 0:
                raw_videos.append(f'https://www.youtube.com{video}')

        if len(raw_videos) > 0:
            youtube.add_value('videos', raw_videos)


        yield youtube.load_item()
