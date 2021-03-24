# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urlparse
import scrapy
import re
import json
from imdb import settings
from scrapy_selenium import SeleniumRequest


class TempeTyresSpider(scrapy.Spider):
    name = 'imdb_contacts'
    file_name = '{}.{}'.format(datetime.now().strftime("%Y%m%d%H%M%S"), settings.FEED_FORMAT)
    TAG_RE = re.compile(r'<[^>]+>')

    def remove_tags(self, text):
        return self.TAG_RE.sub('', text)

    def start_requests(self):
        yield SeleniumRequest(
            url='https://secure.imdb.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.imdb.com%2Fregistration%2Fap-signin-handler%2Fimdb_pro_us&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=imdb_pro_us&openid.mode=checkid_setup&siteState=eyJvcGVuaWQuYXNzb2NfaGFuZGxlIjoiaW1kYl9wcm9fdXMiLCJyZWRpcmVjdFRvIjoiaHR0cHM6Ly9wcm8uaW1kYi5jb20vIn0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0')

    def parse(self, response, **kwargs):
        self.cookies = self.login(response)
        with open('csv/imdb_details/imdb_details.json') as p:
            file_data = json.load(p)
        for data in file_data:
            for user in data['director_data']:
                yield scrapy.Request(url=user['url'].replace('www', 'pro'), callback=self.parse_contact,
                                     meta={'data': data, 'user': user})

    def parse_contact(self, response, **kwargs):
        data = response.meta['data']
        user = response.meta['user']
        contact = dict()
        contact_text = response.css('#contacts > div > div.a-row.header.contacts_header > div > span::text').get(
            '').lower()
        if 'company' in contact_text or 'direct contact' in contact_text:
            ul = response.css('#contacts > div > div.a-section.a-spacing-top-mini > ul:nth-child(1)').get('')
            email = self.find_emails(self.remove_tags(ul))

    def login(self, response):
        user = 'harlow.28@gmail.com'
        password = 'Bunker15Films'
        self.driver = response.meta['driver']
        self.driver.find_element_by_id('ap_email').send_keys(user)
        self.driver.find_element_by_id('ap_password').send_keys(password)
        self.driver.find_element_by_id('signInSubmit').click()
        cookies = self.driver.get_cookies()
        return cookies

    def close(spider, reason):
        spider.driver.get('https://pro.imdb.com/logout?ref_=hm_nv_usr_logout')

    def find_emails(self, text):
        return []
