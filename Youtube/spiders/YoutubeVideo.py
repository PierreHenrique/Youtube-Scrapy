# -*- coding: utf-8 -*-
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
from scrapy import Selector
from Youtube.items import YoutubeVideoItem, YoutubeCommentItem
import json
import time


class YoutubeVideoSpider(CrawlSpider):
    name = 'YoutubeVideo'
    urls = ['https://www.youtube.com/watch?v=qugygyTz-qo']

    script1 = """
        function scroll_to(splash, x, y)
          local js = string.format(
            "window.scrollTo(%s, %s); print(y);", tonumber(x), tonumber(y)
          )
          print(y)
          return splash:runjs(js)
        end
        
        function main(splash)
            local num_scrolls = 20

            splash.http2_enabled = true
            splash.images_enabled  = false
            splash.html5_media_enabled = false
            assert(splash:go(splash.args.url))
            for _ = 1, num_scrolls do
                scroll_to(splash, 0, 999999999999)
                splash:wait(2.0)
            end
            print("Finished")
            return {html=splash:html()}
        end
        """

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
            print('Sending request')
            yield SplashRequest(url, self.parse, endpoint='execute', args={'har': 1,'html': 1,'lua_source': self.script1,'wait': 2.0, 'timeout': 90}, meta={'original_url': url})

    def parse(self, response):
        video = ItemLoader(item=YoutubeVideoItem(), response=response)

        info = response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/div/div[3]/ytd-sentiment-bar-renderer/paper-tooltip/div/text()').get()
        comments = response.xpath('//*[@id="comment"]').getall()

        if info is not None:
            info = info.split("/")

        video.add_value('url', response.meta['original_url'])
        video.add_value('date', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/div/div[1]/div[2]/yt-formatted-string/text()').get())
        video.add_value('title', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/h1/yt-formatted-string/text()').get())
        video.add_value('views', response.xpath('/html/body/ytd-app/div/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[5]/div[2]/ytd-video-primary-info-renderer/div/div/div[1]/div[1]/yt-view-count-renderer/span[1]/text()').get())
        video.add_value('likes', info[0].strip())
        video.add_value('dislikes', info[1].strip())

        for comment in comments:
            s = Selector(text=comment)
            item = ItemLoader(item=YoutubeCommentItem(), response=response)
            url = s.xpath('//*[@id="author-text"]/@href').get()
            item.add_value('url', f'https://www.youtube.com{url}')
            item.add_value('name', self.clean(s.xpath('//*[@id="author-text"]/span/text()').get()))
            item.add_value('picture', s.xpath('//*[@id="img" and @class="style-scope yt-img-shadow"]/@src').get())
            item.add_value('content', s.xpath('//*[@id="content-text"]/text()').get())
            item.add_value('likes', self.clean(s.xpath('//*[@id="vote-count-middle"]/text()').get()))
            item.add_value('dislikes', '0')

            video.add_value('comments', item.load_item())

        yield video.load_item()