import scrapy
from scrapy.crawler import CrawlerProcess
import csv
import os

from imdb_service import get_omdb_rating


class FilmsSpider(scrapy.Spider):
    filename = 'output.csv'
    name = 'films'
    FILMS_PACKAGES_PATTERN = 'div.CategoryTreeItem'
    FILMS_NAMES_PATTERN = '#mw-pages > div > div > div > ul > li'
    FILM_PAGE_PATTERN = '#mw-content-text > div.mw-content-ltr.mw-parser-output > table.infobox > tbody'

    def start_requests(self):
        print('welcome')
        # Проверяем, существует ли файл
        if os.path.exists(self.filename):
            # Если файл существует, удаляем его
            os.remove(self.filename)
        with open(self.filename, 'a', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['title', 'year', 'genre', 'country', 'rating', 'director']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Записываем заголовки столбцов
            writer.writeheader()

        URL = (
            'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%BF%D0%BE_%D0%B3%D0%BE%D0%B4%D0%B0%D0%BC')
        yield scrapy.Request(url=URL, callback=self.parse_films)

    def parse_films(self, response):
        for index, selector in enumerate(response.css(self.FILMS_PACKAGES_PATTERN)):
            if index < 6:  # не берем первые 6 элементов, т.к. они дублируют фильмы
                continue
            next_page = selector.css(self.FILMS_PACKAGES_PATTERN + ' > a::attr(href)').extract_first()
            if next_page:
                yield response.follow(next_page, callback=self.select_page_type)

    def select_page_type(self, response):

        if len(response.css(self.FILMS_NAMES_PATTERN)) > 0:
            for selector in response.css(self.FILMS_NAMES_PATTERN):
                next_page = selector.css('a::attr(href)').extract_first()
                if next_page:
                    yield response.follow(next_page, callback=self.select_page_type)

        elif len(response.css(self.FILM_PAGE_PATTERN)) > 0:
            for selector in response.css(self.FILM_PAGE_PATTERN):
                title = selector.css('th.infobox-above::text').extract_first()

                year = selector.css('span.dtstart::text').extract_first()
                if year is None:
                    year = selector.css('td > span > span > span.nowrap > a::text').extract_first()

                genre = selector.css('td > span[data-wikidata-property-id="P136"] > a::text').extract_first()
                if genre is None:
                    genre_list = selector.css('td > span[data-wikidata-property-id="P136"] [title]').getall()
                    genre = ', '.join([element.split('title="')[1].split('"')[0] for element in genre_list])
                if genre is None:
                    genre_list = selector.css('td > span[data-wikidata-property-id="P136"] > ul > li [title]').getall()
                    genre = ', '.join([element.split('title="')[1].split('"')[0] for element in genre_list])

                country = selector.css('span.country-name > span > a::text').extract_first()
                if country is None:
                    country = selector.css('td > span[data-wikidata-property-id="P495"] > span > a > span::text').extract_first()
                if country is None:
                    country = selector.css('td > span[data-wikidata-property-id="P495"] > a::text').extract_first()

                director = selector.css('tr > td > span[data-wikidata-property-id="P57"] > a::text').extract_first()
                if director is None:
                    director = selector.css('tr > td > span[data-wikidata-property-id="P57"]::text').extract_first()
                if director is None:
                    director = selector.css('td > ul > li > span > span > span > a > span::text').extract_first()


                eng_title = selector.css('td > span > span::text').extract_first()
                rating = get_omdb_rating(eng_title)

                if rating is None: # при исчерпании лимита - проставляется ноль
                    rating = 0

                # Создаем файл и записываем данные
                with open(self.filename, 'a', newline='', encoding='utf-8') as csv_file:
                    fieldnames = ['title', 'year', 'genre', 'country', 'rating', 'director']
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                    # Записываем данные
                    writer.writerow({'title': title, 'year': year, 'genre': genre, 'country': country, 'rating': rating, 'director': director})


process = CrawlerProcess()
process.crawl(FilmsSpider)
process.start()
