import re

import scrapy

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import TatrabankaskItem
from itemloaders.processors import TakeFirst


class TatrabankaskSpider(scrapy.Spider):
	name = 'tatrabankask'
	start_urls = ['https://www.tatrabanka.sk/sk/blog/tlacove-spravy/',
	              'https://www.tatrabanka.sk/sk/blog/',
	              'https://www.tatrabanka.sk/sk/o-banke/novinky-oznamy/',
	              ]

	def parse(self, response):
		post_links = response.xpath('//div[@class="article"]//a/@href').getall()
		print(post_links)
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@rel="next"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="col-sm-8"]//text()[normalize-space() and not(ancestor::h1 | ancestor::p[contains(@class, "smallest")] | ancestor::button)]').getall()
		description = [remove_tags(p).strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="col-sm-8"]/p[contains(@class, "smallest")]/text()[normalize-space()]').get()
		if date:
			date = re.findall(r'\d+\.\d+\.\d+', date)

		item = ItemLoader(item=TatrabankaskItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
