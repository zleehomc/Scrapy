import json
import scrapy
from scrapy import Request
from lxml import etree
from foursquare.items import FoursquareItem


class DmozSpider(scrapy.Spider):
    name = "fs"
    allowed_domains = ["foursquare.com"]
    start_urls = [
        "https://foursquare.com/user/1719059",
    ]
    wsid = 'R2ABUMCA2PJ5TD5V2KHEWGCIEGPDP5'
    token = 'QEJ4AQPTMMNB413HGNZ5YDMJSHTOHZHMLZCAQCCLXIX41OMP'
    limit = 197
    priority_this = 100000

    def parse(self, response):
        item_top_new = FoursquareItem()
        item_top_new['id'] = "30562435"
        item_top_new['contact'] = {}
        priority_t = self.priority_this
        item_top_new['deep'] = 1
        yield Request(url=self.get_url(item_top_new['id'], "tips"),
                      meta={'item': item_top_new,
                            'priority': priority_t},
                      callback=self.parse_tips)

    def parse_tips(self, response):
        body = json.loads(response.body)
        item_top = response.meta['item']
        priority_t = response.meta['priority']
        item_tips = []
        for tip in body['response']['tips']['items']:
            combo_location = str(tip['venue']['location'][
                'lat']) + ',' + str(tip['venue']['location']['lng'])
            if combo_location not in item_tips:
                item_tips.append(combo_location)
        item_top['position_tips'] = item_tips
        item_follower = []
        item_contact = []
        yield Request(url=self.get_url(item_top['id'], "followers"),
                      meta={'item': item_top,
                            'priority': priority_t,
                            'item_follower': item_follower,
                            'item_contact': item_contact},
                      callback=self.parse_follower,
                      priority=priority_t)

    def parse_follower(self, response):
        body = json.loads(response.body)
        if(body['response']['followers']['count'] <= 10000):
            priority_t = response.meta['priority']
            item_top = response.meta['item']
            item_follower = response.meta['item_follower']
            item_contact_follower = response.meta['item_contact']
            for user in body['response']['followers']['items']:
                item_follower.append(user['user']['id'])
                item_contact_follower.append(user['user']['contact'])
            if(body['response']['moreData']):
                trailingMarker = body['response']['trailingMarker']
                yield Request(url=self.get_url(item_top['id'], "followers", trailingMarker),
                              meta={'item': item_top,
                                    'priority': priority_t,
                                    'item_follower': item_follower,
                                    'item_contact': item_contact_follower},
                              callback=self.parse_follower,
                              priority=priority_t)
            else:
                item_top['followers'] = item_follower
                item_contact = []
                item_following = []
                yield Request(url=self.get_url(item_top['id'], "following"),
                              meta={'item': item_top,
                                    'item_contact_follower': item_contact_follower,
                                    'item_following': item_following,
                                    'item_contact': item_contact,
                                    'priority': priority_t},
                              callback=self.parse_following,
                              priority=priority_t)

    def parse_following(self, response):
        body = json.loads(response.body)
        item_top = response.meta['item']
        priority_t = response.meta['priority']
        item_contact_follower = response.meta['item_contact_follower']
        item_following = response.meta['item_following']
        item_contact = response.meta['item_contact']
        for user in body['response']['following']['items']:
            item_following.append(user['user']['id'])
            item_contact.append(user['user']['contact'])
        if(body['response']['moreData']):
            trailingMarker = body['response']['trailingMarker']
            yield Request(url=self.get_url(item_top['id'], "following", trailingMarker),
                          meta={'item': item_top,
                                'item_contact_follower': item_contact_follower,
                                'item_following': item_following,
                                'item_contact': item_contact,
                                'priority': priority_t},
                          callback=self.parse_following,
                          priority=priority_t)
        else:
            item_top['following'] = item_following
            yield item_top
            priority_t = priority_t - 1
            priority_following = priority_t
            priority_follower = priority_t
            for i in range(len(item_top['following'])):
                priority_follower = priority_follower
                item_top_new = FoursquareItem()
                item_top_new['deep'] = item_top['deep'] + 1
                item_top_new['id'] = item_top['following'][i]
                item_top_new['contact'] = item_contact[i]
                yield Request(url=self.get_url(item_top_new['id'], "tips"),
                              meta={'item': item_top_new,
                                    'priority': priority_t},
                              callback=self.parse_tips,
                              priority=priority_follower)
            for i in range(len(item_top['followers'])):
                priority_following = priority_following
                item_top_new = FoursquareItem()
                item_top_new['deep'] = item_top['deep'] + 1
                item_top_new['id'] = item_top['followers'][i]
                item_top_new['contact'] = item_contact_follower[i]
                yield Request(url=self.get_url(item_top_new['id'], "tips"),
                              meta={'item': item_top_new,
                                    'priority': priority_t},
                              callback=self.parse_tips,
                              priority=priority_following)

    def get_url(self, id, type, afterMarker=""):
        return 'https://api.foursquare.com/v2/users/' + id + "/" + type + "?locale=en&explicit-lang=false&v=20170530&id=" + id + "&limit=" + str(self.limit) + "&afterMarker=" + afterMarker + "&m=foursquare&wsid=" + self.wsid + "&oauth_token=" + self.token
