# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urlparse
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
        "https://pro.imdb.com/inproduction/_paginated?offset={}&count=100&q=&ref=undefined&keyspace=TITLE&type=movie&status=POST_PRODUCTION,RELEASED&year=2020-2022&sort=ranking")

    def start_requests(self):
        yield SeleniumRequest(
            url='https://secure.imdb.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.imdb.com%2Fregistration%2Fap-signin-handler%2Fimdb_pro_us&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=imdb_pro_us&openid.mode=checkid_setup&siteState=eyJvcGVuaWQuYXNzb2NfaGFuZGxlIjoiaW1kYl9wcm9fdXMiLCJyZWRpcmVjdFRvIjoiaHR0cHM6Ly9wcm8uaW1kYi5jb20vIn0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0')

    def parse(self, response, **kwargs):
        self.cookies = self.login(response)
        yield SeleniumRequest(url=self.movie_api.format(0), callback=self.parse_movie_list, meta={'offset': 0})

    def parse_movie_list(self, response, **kwargs):
        offset = response.meta['offset']
        # yield SeleniumRequest(url=self.movie_api.format(offset), meta={'offset': offset}, callback=self.parse_movie_list)
        # selector = 'li' if offset > 100 else '#results > li'
        if offset < 100:
            for movie in response.css('#results > li')[:5]:
                data = dict(
                    title=movie.css('span.display-title > a::text').get(),
                    url=movie.css('span.display-title > a::attr(href)').get(),
                    country=movie.css('ul.title > li:contains("Country")::text').get('').split(',')[0].split(':')[
                                -1].strip() or
                            movie.css('ul.title > li:contains("Country")::text').get('').split(',')[0].split(':')[
                                -1].strip(),
                    genre=', '.join(movie.css('ul.title > li:contains("Genre")::text').extract()).strip().split(':')[
                        -1],
                    year=movie.css('span.year::text').get('').replace('(', '').replace(')', ''),
                    gross=movie.css('span.us_gross::text').get('').strip(),
                    budget=movie.css('span.budget_usd::text').get('').strip()
                )
                data['path'] = urlparse(data.get('url')).path
                yield data
                # yield SeleniumRequest(url=f'https://www.imdb.com{data["path"]}fullcredits',
                #                       callback=self.parse_movie_details, dont_filter=True,
                #                       meta={'data': data})
            offset += 100
            yield SeleniumRequest(url=self.movie_api.format(offset), meta={'offset': offset},
                                  callback=self.parse_movie_list)

        else:
            movie = False
            for movie in response.css('li'):
                if movie.css('ul li span.display-title > a::text').get():
                    data = dict(
                        title=movie.css('ul li span.display-title > a::text').get(),
                        url=movie.css('ul li span.display-title > a::attr(href)').get(),
                        genre=
                        ', '.join(movie.css('ul li:last-child::text').extract()).strip().split(':')[-1],
                        year=movie.css('span.year::text').get('').replace('(', '').replace(')', ''),
                        country=
                        movie.css('ul.title > li > span > span:contains("Country")::text').get('').split(',')[0].split(
                            ':')[-1].strip() or
                        movie.css('ul.title > li > span > span:contains("Countries")::text').get('').split(',')[
                            0].split(':')[-1].strip(),
                        gross=movie.css('span.us_gross::text').get('').strip(),
                        budget=movie.css('span.budget_usd::text').get('').strip(),
                    )
                    data['path'] = urlparse(data.get('url')).path
                    yield data
                    # yield SeleniumRequest(url=f'https://www.imdb.com{data["path"]}fullcredits',
                    #                       callback=self.parse_movie_details,
                    #                       dont_filter=True, meta={'data': data})

            if movie:
                offset += 100
                yield SeleniumRequest(url=self.movie_api.format(offset), meta={'offset': offset},
                                      callback=self.parse_movie_list)

    def parse_movie_details(self, response, **kwargs):
        d_data = []
        for tr in response.css('#director ~table:nth-child(2) tbody tr'):
            d_data.append(dict(
                name=tr.css('td.name > a::text').get('').strip(),
                url=response.urljoin(tr.css('td.name > a::attr(href)').get('').strip()),
                title=tr.css('td.credit::text').get('').strip()
            ))

        w_data = []
        for tr in response.css('#writer ~table:nth-child(4) tbody tr'):
            w_data.append(dict(
                name=tr.css('td.name > a::text').get('').strip(),
                url=response.urljoin(tr.css('td.name > a::attr(href)').get('').strip()),
                title=tr.css('td.credit::text').get('').strip()
            ))

        data = response.meta['data']
        data.update(dict(
            directed_by=d_data,
            writer=w_data,
        ))
        yield SeleniumRequest(url=f'https://www.imdb.com{data["path"]}releaseinfo',
                              callback=self.parse_movie_release_date,
                              dont_filter=True, meta={'data': data})

    def parse_movie_release_date(self, response, **kwargs):
        data = response.meta['data']
        w_data = []
        for tr in response.css('#releases ~table:nth-child(4) tbody tr'):
            w_data.append(dict(
                country=tr.css('td.release-date-item__country-name > a::text').get('').strip(),
                date=tr.css('td.release-date-item__date::text').get('').strip(),
                title=tr.css('td.release-date-item__attributes::text').get('').strip()
            ))
        data.update(dict(release_dates=w_data))
        yield SeleniumRequest(url=f'https://www.imdb.com{data["path"]}companycredits',
                              callback=self.parse_movie_company_credits,
                              dont_filter=True, meta={'data': data})

    def parse_movie_company_credits(self, response, **kwargs):
        p_data = []
        for li in response.css('#production ~ul:nth-child(3) > li'):
            p_data.append(dict(
                company_url=response.urljoin(li.css('a::attr(href)').get()),
                company=li.css('a::text').get()
            ))
        d_data = []
        for li in response.css('#production ~ul:nth-child(5) > li'):
            d_data.append(dict(
                company_url=response.urljoin(li.css('a::attr(href)').get()),
                company=li.css('a::text').get(),
                details=li.css('::text').extract()[-1].strip()
            ))
        data = response.meta['data']
        data.update(dict(
            production_data=p_data,
            distributors_data=d_data,
        ))
        yield SeleniumRequest(url=f'https://www.imdb.com{data["path"]}awards', callback=self.parse_movie_details,
                              dont_filter=True, meta={'data': data})

    def parse_movie_awards(self, response, **kwargs):
        data = response.meta['data']
        data.update(dict(
            directed_by=response.css('#director ~table tbody tr td.name a::text').get(),
            director_url=response.css('#director ~table tbody tr td.name a::attr(href)').get(),
        ))
        yield SeleniumRequest(url=f'https://www.imdb.com{data["path"]}releaseinfo', callback=self.parse_movie_details,
                              dont_filter=True, meta={'data': data})

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
