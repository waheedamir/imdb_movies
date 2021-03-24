# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urlparse
import scrapy
import json
from imdb import settings


class TempeTyresSpider(scrapy.Spider):
    name = 'imdb_details'
    file_name = '{}.{}'.format(datetime.now().strftime("%Y%m%d%H%M%S"), settings.FEED_FORMAT)

    def start_requests(self):
        with open('csv/imdb/imdb_20210320154004.json') as p:
            file_data = json.load(p)
        for data in file_data:
            data['path'] = urlparse(data.get('url')).path
            yield scrapy.Request(url=f'https://www.imdb.com{data["path"]}fullcredits',
                                 meta={'data': data})

    def parse(self, response, **kwargs):
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
        p_data = []
        for tr in response.css('#producer ~table:nth-child(8) tbody tr'):
            p_data.append(dict(
                name=tr.css('td.name > a::text').get('').strip(),
                url=response.urljoin(tr.css('td.name > a::attr(href)').get('').strip()),
                title=tr.css('td.credit::text').get('').strip()
            ))

        data = response.meta['data']
        data.update(dict(
            director_data=d_data,
            writer_data=w_data,
            producer_data=p_data
        ))
        yield scrapy.Request(url=f'https://www.imdb.com{data["path"]}releaseinfo',
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
        yield scrapy.Request(url=f'https://www.imdb.com{data["path"]}companycredits',
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
        yield scrapy.Request(url=f'https://www.imdb.com{data["path"]}awards', callback=self.parse_movie_awards,
                             dont_filter=True, meta={'data': data})

    def parse_movie_awards(self, response, **kwargs):
        data = response.meta['data']
        tables = response.css('#main > div > div.article > table.awards')
        headings = response.css('#main > div > div.article > h3')
        a_data = []
        for heading, table in zip(headings, tables):
            a_data.append(dict(
                title=' '.join(heading.css('::text').extract()).strip(),
                result=' '.join(table.css('td.title_award_outcome > b::text').extract()).strip()
            ))
        data.update(dict(awards=a_data))
        yield data
