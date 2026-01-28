# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyMoviesItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    genres = scrapy.Field()
    directors = scrapy.Field()
    countries = scrapy.Field()
    year = scrapy.Field()
    rating = scrapy.Field()
    pass
