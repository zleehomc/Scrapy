# -*- coding: utf-8 -*-

from scrapy import Selector
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from tw.items import TwItem


class TwSpiderSpider(CrawlSpider):
    name = 'tw_spider'
    allowed_domains = ['blog.csdn.net']
    start_urls = ['http://blog.csdn.net/u012150179/article/details/11749017']
    rules = [
        Rule(LinkExtractor(allow=('/u012150179/article/details'),
                               restrict_xpaths=('//li[@class="next_article"]')),
             callback='parse_item',
             follow=True)
    ]

    def parse_item(self, response):

        item = TwItem()
        sel = Selector(response)
        blog_url = str(response.url)
        blog_name = sel.xpath('//div[@id="article_details"]/div/h1/span/a/text()').extract()
        item['blog_name'] = [n for n in blog_name]
        item['blog_url'] = blog_url
        yield item