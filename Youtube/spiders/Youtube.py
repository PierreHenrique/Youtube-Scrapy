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
            local num_scrolls = 30
                
            splash.http2_enabled = true
            splash.images_enabled  = true
            splash.html5_media_enabled = true
            assert(splash:go(splash.args.url))
            splash:wait(3.0)
            for _ = 1, num_scrolls do
                splash:runjs("window.scrollTo(0, 999999999);")
                splash:wait(0.4)
            end
            print("Finished")
            return {html=splash:html()}
        end
        """

    def start_requests(self):
        yield SplashRequest('https://www.youtube.com/user/ElectronicDesireGE/videos', self.parse, endpoint='execute', args={'har': 1,'html': 1,'lua_source': self.script1})

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
