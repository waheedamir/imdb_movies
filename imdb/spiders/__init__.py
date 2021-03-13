# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
from scrapy_selenium import SeleniumRequest

from imdb import settings


class TempeTyresSpider(scrapy.Spider):
    name = 'imdb'
    driver = None
    cookies = None
    file_name = '{}.{}'.format(datetime.now().strftime("%Y%m%d%H%M%S"), settings.FEED_FORMAT)
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_selenium.SeleniumMiddleware': 800
        }
    }

    movie_api = (
        "https://pro.imdb.com/inproduction/development/_paginated?offset={}&count=100&q=&ref=undefined&keyspace=TITLE&type=movie&sort=ranking")

    def start_requests(self):
        yield SeleniumRequest(
            url='https://secure.imdb.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.imdb.com%2Fregistration%2Fap-signin-handler%2Fimdb_pro_us&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=imdb_pro_us&openid.mode=checkid_setup&siteState=eyJvcGVuaWQuYXNzb2NfaGFuZGxlIjoiaW1kYl9wcm9fdXMiLCJyZWRpcmVjdFRvIjoiaHR0cHM6Ly9wcm8uaW1kYi5jb20vIn0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0')

    def parse(self, response, **kwargs):
        self.cookies = self.login(response)
        yield SeleniumRequest(url=self.movie_api.format(0), callback=self.parse_movie_list, meta={'offset': 0})

    def parse_movie_list(self, response, **kwargs):
        offset = response.meta['offset'] + 100
        yield SeleniumRequest(url=self.movie_api.format(offset), meta={'offset': offset}, callback=self.parse_movie_list)
        # selector = 'li' if offset > 100 else '#results > li'
        if offset < 100:
            for movie in response.css('#results > li'):
                yield dict(
                    title=movie.css('span.display-title > a::text').get(),
                    url=movie.css('span.display-title > a::attr(href)').get(),
                    genre=', '.join(movie.css('ul.title > li:contains("Genre")::text').extract()).strip().split(':')[
                        -1],
                    year=movie.css('span.year::text').get('').replace('(', '').replace(')', '')
                )
            yield SeleniumRequest(url=self.movie_api.format(offset), meta={'offset': offset},
                                  callback=self.parse_movie_list)

        else:
            for movie in response.css('li'):
                if movie.css('ul li span.display-title > a::text').get():
                    yield dict(
                        title=movie.css('ul li span.display-title > a::text').get(),
                        url=movie.css('ul li span.display-title > a::attr(href)').get(),
                        genre=
                        ', '.join(movie.css('ul li:last-child::text').extract()).strip().split(':')[-1],
                        year=movie.css('span.year::text').get('').replace('(', '').replace(')', '')
                    )
            yield SeleniumRequest(url=self.movie_api.format(offset), meta={'offset': offset},
                                  callback=self.parse_movie_list)

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
