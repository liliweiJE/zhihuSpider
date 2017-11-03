# -*- coding: utf-8 -*-
import scrapy,urllib,re
from scrapy.http import Request, FormRequest
import time
from CartoonSpider.items import *
from PIL import Image
import json
import requests

class CookieZhiHuSpider(scrapy.Spider):
    name="CookieSpider"
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    headers_zhihu = {
           'Host':'www.zhihu.com ',
           'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
           'Accept-Encoding':'gzip,deflate,sdch',
           'Referer':'https://www.zhihu.com ',
           'If-None-Match':"FpeHbcRb4rpt_GuDL6-34nrLgGKd.gz",
           'Cache-Control':'max-age=0',
           'Connection':'keep-alive'
    }

    def start_requests(self):
        return [
            Request("https://www.zhihu.com/", meta={'cookiejar': 1}, headers=self.headers_zhihu, callback=self.captcha)]

    def captcha(self, response):
        xsrf = response.xpath('//input[@name="_xsrf"]/@value').extract()[0]
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + '&type=login&lang=en'
        return [Request(captcha_url, callback=self.parser_captcha,
                        meta={'cookiejar': response.meta['cookiejar'], 'xsrf': xsrf})]

    def parser_captcha(self, response):
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
            f.close()
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
        captcha = input("请输入验证码：")
        xsrf = response.meta['xsrf']
        return FormRequest('https://www.zhihu.com/login/email',
                           method='POST',
                           meta={'cookiejar': response.meta['cookiejar']},
                           callback=self.after_login,
                           dont_filter=True,
                           headers=self.headers_zhihu,
                           formdata={
                               'email': '2264116263@qq.com',
                               'password': '2264116263',
                               '_xsrf': xsrf,
                               'captcha_type': 'en',
                               'captcha': captcha,
                           }, )

    def after_login(self, response):
        json_file = json.loads(response.text)
        print (json_file)
        if json_file['r'] == 0:
            print('登录成功.....开始爬了。。。。')
            yield Request(
                    'http://www.zhihu.com',
                    meta={'cookiejar': response.meta['cookiejar']},
                    headers=self.headers_zhihu,
                    callback=self.parse,
                    dont_filter=True,
                )
        else:
            print('登录失败！')

    def parse(self, response):
        print(response.se)
        leirong = response.xpath('//div[@class="Card TopstoryItem"]')
        print(len(leirong))
        for lr in leirong:
            #print(lr.extract())
            author = lr.xpath('.//div//div[2]//div[@class="AuthorInfo-content"]//a//text()').extract()
            title = lr.xpath('.//div//div[3]//h2[@class="ContentItem-title"]//a//text()').extract()
            if len(author)==0 and len(title)==0:
                continue
            elif len(author)==0:
                print("作者：匿名用户")
                print("标题：%s" % title)
            else:
                print("作者：%s" % author)
                print("标题：%s" % title)


