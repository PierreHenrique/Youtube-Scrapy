# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider
from scrapy import Selector

from Youtube.SeleniumRequest import SeleniumRequest
from Youtube.items import YoutubeVideoItem, YoutubeCommentItem, YoutubeFeedItem, YoutubeChannelItem
from selenium import webdriver

class YoutubeVideoSpider(CrawlSpider):
    name = 'YoutubeFeed'
    urls = ['https://www.youtube.com/channel/UC7g0L0zxkDw9cpRTXR1z0yg/feed']

    def clean(self, word):
        if word is not None:
            return word.replace('\n', ' ').strip()
        else:
            return ''


    def start_requests(self):
        for url in self.urls:
            yield SeleniumRequest(url=url, callback=self.parse_item, endless_scrolling='//ytd-channel-renderer[@class="style-scope ytd-feed-entry-renderer"]', experimental='//ytd-video-renderer[@class="style-scope ytd-feed-entry-renderer"]')

    def parse_item(self, response):
        feed = ItemLoader(item=YoutubeFeedItem(), response=response)

        channels = response.xpath('//ytd-item-section-renderer[@class="style-scope ytd-section-list-renderer"]').getall()

        feed.add_value('id', response.request.url)

        for channel in channels:
            s = Selector(text=channel)

            if s.xpath('//a[@id="main-link"]/@href').get() is not None:
                item = ItemLoader(item=YoutubeChannelItem(), response=response)
                item.add_value('id', s.xpath('//a[@id="main-link"]/@href').get())
                item.add_value('name', self.clean(s.xpath('//div[@class="style-scope ytd-channel-name"]/div/yt-formatted-string/text()').get()))
                item.add_value('videos', s.xpath('//span[@id="video-count"]/text()').get())
                item.add_value('subscribers', self.clean(s.xpath('//span[@id="subscribers"]/text()').get()))

                feed.add_value('channels', item.load_item())


        yield feed.load_item()