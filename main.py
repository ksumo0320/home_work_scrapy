import scrapy
from scrapy.crawler import CrawlerProcess


class FilmsSpider(scrapy.Spider):
    name = 'films'
    FILMS_PACKAGES_PATTERN = 'div.CategoryTreeItem'
    FILMS_NAMES_PATTERN = '#mw-pages > div > div > div > ul > li'

    def start_requests(self):
        URL = (
            'https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%BF%D0%BE_%D0%B3%D0%BE%D0%B4%D0%B0%D0%BC')
        yield scrapy.Request(url=URL, callback=self.parse_films)

    def parse_films(self, response):
        for selector in response.css(self.FILMS_PACKAGES_PATTERN):
            yield {
                # titles from main page
                'title': selector.css(self.FILMS_PACKAGES_PATTERN + ' > a::text').extract_first()
            }

            next_page = selector.css(self.FILMS_PACKAGES_PATTERN + ' > a::attr(href)').extract_first()
            if next_page:
                yield response.follow(next_page, callback=self.select_page_type)

    def select_page_type(self, response):
        if len(response.css(self.FILMS_NAMES_PATTERN)) > 0:
            for selector in response.css(self.FILMS_NAMES_PATTERN):
                yield {
                    'title': selector.css('a::text').extract_first()  # films names
                }
                # TODO next_page for film page
        elif len(response.css(self.FILMS_PACKAGES_PATTERN)) > 0:
            for selector in response.css(self.FILMS_PACKAGES_PATTERN):
                yield {
                    # titles from child pages with films packages f.e. 1890 films
                    'title': selector.css(self.FILMS_PACKAGES_PATTERN + ' > a::text').extract_first()
                }
                next_page = selector.css(self.FILMS_PACKAGES_PATTERN + ' > a::attr(href)').extract_first()
                if next_page:
                    yield response.follow(next_page, callback=self.select_page_type)
        # TODO elif for film page (show title, genre, director, country, year...)
        # TODO csv output


process = CrawlerProcess()
process.crawl(FilmsSpider)
process.start()
