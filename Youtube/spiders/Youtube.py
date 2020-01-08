# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
from Youtube.items import YoutubeItem


class YoutubeSpider(CrawlSpider):
    name = 'Youtube'

    script1 = """
        function main(splash)
            assert(splash:go(splash.args.url))
            splash.http2_enabled = true
            splash:wait(splash.args.wait)
            return {html=splash:html()}
        end
        """

    def start_requests(self):
        yield SplashRequest('https://www.youtube.com/user/ElectronicDesireGE/videos', self.parse, endpoint='execute', args={'har': 1,'html': 1,'lua_source': self.script1,'wait': 0.2})

    def parse(self, response):
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
