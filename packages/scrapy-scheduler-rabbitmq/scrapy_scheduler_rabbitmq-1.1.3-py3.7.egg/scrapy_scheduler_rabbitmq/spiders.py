# -*- coding: utf-8 -*-
import scrapy
import pickle
import json
from scrapy.utils.reqser import request_from_dict


class RabbitSpider(scrapy.Spider):
    def _make_request(self, mframe, hframe, body):

        data = json.loads(body,encoding="utf-8")
        data['params']['pyppeteer'] = True
        request = scrapy.Request(data['url'], callback=self.parse, dont_filter=True,meta=data['params'])

        return request
