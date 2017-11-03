import scrapy
import time
from scrapy.http import Request, FormRequest
from PIL import Image
import json

class ZhiHuSpider(scrapy.Spider):
    name='ZhiHuSpider'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/']

    def start_requests(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + '&type=login&lang=en'
        return [Request(captcha_url, callback=self.parser_captcha)]


    def parser_captcha(self, response):
        with open('captcha.jpg', 'wb') as f:
            f.write(response.body)
            f.close()
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
        captcha = input("input the captcha with quotation mark\n>")
        return Request(url='https://www.zhihu.com/', callback=self.login, meta={'captcha': captcha})


    def login(self, response):
        xsrf = response.xpath('//input[@name="_xsrf"]/@value').extract()[0]
        print ('xsrf:' + xsrf)
        print (response.meta['captcha'])
        return [FormRequest('https://www.zhihu.com/login/email',
                            method='POST',
                            formdata={
                                'email': '2264116263@qq.com',
                                'password': '2264116263',
                                '_xsrf': xsrf,
                                'captcha_type': 'en',
                                'captcha': response.meta['captcha'],
                            },

                            callback=self.after_login,
                            )]

    def after_login(self, response):
        json_file = json.loads(response.text)
        if json_file['r'] == 0:
            print('success........登录成功')
            yield Request(
                'http://www.zhihu.com',
                #meta={'cookiejar': response.meta['cookiejar']},
                #headers=self.headers_zhihu,
                callback=self.parse,
                dont_filter=True,
            )
        else:
            print('登录失败！')
            print(response)

    def parse(self, response):
        print(response.text)
        leirong = response.xpath('//div[@class="Card TopstoryItem"]')
        for lr in leirong:
            author = lr.xpath('.//div[@class="AuthorInfo-content"]/div[1]/span/div/div/a/text()').extract()
            #title = lr.xpath('.//div[@class="ContentItem AnswerItem"]/h2/div/a/text()').extract()
            print ("作者：%s" % author.encode('utf-8'))
           # print ("标题：%s" % title.encode('utf-8'))
