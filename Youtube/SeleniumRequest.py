from scrapy import Request


class SeleniumRequest(Request):
    def __init__(self, endless_scrolling=None, *args, **kwargs):

        self.endless_scrolling = endless_scrolling

        super().__init__(*args, **kwargs)