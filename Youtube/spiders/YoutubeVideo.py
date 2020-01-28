# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
from scrapy import Selector

from Youtube.SeleniumRequest import SeleniumRequest
from Youtube.items import YoutubeVideoItem, YoutubeCommentItem
from selenium import webdriver

class YoutubeVideoSpider(CrawlSpider):
    name = 'YoutubeVideo'
    urls = ['https://www.youtube.com/watch?v=vw40jqnDuLE']

    '''
        def __init__(self):
        print("Help")
        with open("Youtube.json", "r+") as json_file:
            data = json.load(json_file)
            for url in data[0]['videos']:
                if len(self.urls) < 4:
                    self.urls.append(url)
    '''

    def clean(self, word):
        if word is not None:
            return word.replace('\n', ' ').strip()
        else:
            return ''


    def start_requests(self):
        for url in self.urls:
            yield SeleniumRequest(url=url, callback=self.parse_item, endless_scrolling='//*[@id="content-text"]')

    def parse_item(self, response):
        video = ItemLoader(item=YoutubeVideoItem(), response=response)

        info = response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/div/div[3]/ytd-sentiment-bar-renderer/paper-tooltip/div/text()').get()
        comments = response.xpath('//*[@id="body"]').getall()

        if info is not None:
            info = info.split("/")

        video.add_value('url', '')
        video.add_value('date', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/div/div[1]/div[2]/yt-formatted-string/text()').get())
        video.add_value('title', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/h1/yt-formatted-string/text()').get())
        video.add_value('views', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/div/div[1]/div[1]/yt-view-count-renderer/span[1]/text()').get())

        if info is None:
            info = []
            for i in range(0, 2):
                info.append("0")

        video.add_value('likes', info[0].strip())

        for comment in comments:
            s = Selector(text=comment)
            item = ItemLoader(item=YoutubeCommentItem(), response=response)
            url = s.xpath('//*[@id="author-text"]/@href').get()
            item.add_value('url', f'https://www.youtube.com{url}')
            item.add_value('name', self.clean(s.xpath('//*[@id="author-text"]/span/text()').get()))
            item.add_value('picture', s.xpath('//div[@id="author-thumbnail"]/a/yt-img-shadow/img/@src').get())
            item.add_value('content', s.xpath('//*[@id="content-text"]/text()').get())
            item.add_value('likes', self.clean(s.xpath('//*[@id="vote-count-middle"]/text()').get()))

            video.add_value('comments', item.load_item())

        yield video.load_item()