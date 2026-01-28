# pip install git+https://github.com/cinemagoer/cinemagoer
import scrapy
import re
from imdb import Cinemagoer


class MoviesSpider(scrapy.Spider):
    name = "movies"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ia = Cinemagoer()

    async def start(self):
        url = "https://ru.wikipedia.org/w/index.php?title=%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%A1%D0%A8%D0%90_2007_%D0%B3%D0%BE%D0%B4%D0%B0&pageuntil=%D0%A0%D1%8D%D0%BD%D0%B4%D0%B8+%D0%B8+%D0%BC%D0%B0%D1%84%D0%B8%D1%8F#mw-pages"
        yield scrapy.Request(url=url, callback=self.response_parser)

    def response_parser(self, response):
        for selector in response.css('div.mw-category-group'):
            for partial_link in selector.css('a::attr(href)').getall():
                link = 'https://ru.wikipedia.org' + partial_link
                yield scrapy.Request(url=link, callback=self.parse_page)

            next_page_link = response.css("#mw-pages a[href*='pagefrom=']::attr(href)").get()
            if next_page_link:
                yield response.follow(next_page_link, callback=self.response_parser)

    def parse_page(self, response):
        for selector in response.css('table.infobox'):

            title = selector.css('th.infobox-above::text').extract_first()
            if title is None or title == ' ':
                try:
                    title = selector.css('th > span::text').extract_first()
                except:
                    break

            genres = selector.css("*[data-wikidata-property-id='P136'] a::text").getall()
            genres = [g for g in genres if len(g) > 1]
            genres = [g for g in genres if g not in "[…]"]

            if genres is None:
                for tr in selector.css("table.infobox tr"):
                    head = " ".join(h.strip() for h in tr.css("th *::text, th::text").getall() if h and h.strip())
                    if head == "Жанр" or head == 'Жанры':
                        genres = " ".join(x.strip() for x in tr.css("td *::text").getall() if x and x.strip())
                        break

            directors = selector.css("*[data-wikidata-property-id='P57'] a::text").getall()
            if directors is None or len(directors) == 0:
                directors = selector.css("span[data-wikidata-property-id='P57']::text").getall()
            directors = [d for d in directors if len(d) > 1]
            directors = [d for d in directors if d not in "[…]"]

            countries = selector.css("*[data-wikidata-property-id='P495'] a *::text").getall()
            countries = [c for c in countries if len(c) > 1]

            year = selector.css('span.dtstart::text').extract_first()
            year_re = re.compile(r"\b(?:18|19|20)\d{2}\b")

            if year is None:
                year = selector.css("*[data-wikidata-property-id='P577'] a::text").getall()
                year_text = ' '.join(year)
                t = year_re.search(year_text)
                year = t.group(0) if t else None

            if year is None:
                for tr in selector.css("table.infobox tr"):
                    head = " ".join(h.strip() for h in tr.css("th *::text, th::text").getall() if h and h.strip())
                    if head == "Год" or head == 'Дата выхода':
                        cell = " ".join(x.strip() for x in tr.css("td *::text").getall() if x and x.strip())
                        m = year_re.search(cell)
                        year = m.group(0) if m else None
                        break

            rating = None
            imdb_link = selector.css("span[data-wikidata-property-id='P345'] a::attr(href)").extract_first()
            if imdb_link is not None:
                imdb_link_re = re.compile(r"/title/tt(\d+)/")
                m = imdb_link_re.search(imdb_link)
                imdb_id = m.group(1) if m else None
                if imdb_id is not None:
                    try:
                        movie = self.ia.get_movie(imdb_id)
                        rating = movie.get('rating')
                    except Exception:
                        rating = None
                else:
                    rating = None

            fields = [title, genres, directors, countries, year]
            empty = sum(1 for f in fields if (f is None) or (f=='') or (f==' ') or (isinstance(f, list) and len(f) == 0))
            if empty < 3:
                yield {
                    'Название': title,
                    'Жанры': genres,
                    'Режиссер': directors,
                    'Страны': countries,
                    'Год': year,
                    'Рейтинг': rating
                }
