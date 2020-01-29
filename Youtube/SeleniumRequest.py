from scrapy import Request


class SeleniumRequest(Request):
    def __init__(self, endless_scrolling=None, experimental=None, *args, **kwargs):

        self.endless_scrolling = endless_scrolling
        self.experimental = experimental

        super().__init__(*args, **kwargs)