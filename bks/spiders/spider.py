import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import BksItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class BksSpider(scrapy.Spider):
	name = 'bks'
	start_urls = ['https://www.bks.at/news-presse?p_p_id=com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_4rRcEEkoXQ5d&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_4rRcEEkoXQ5d_delta=10&p_r_p_resetCur=false&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_4rRcEEkoXQ5d_cur=1']
	page_number = 2
	def parse(self, response):
		post_links = response.xpath('//a[@class="news-item-btn btn btn-default"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		# pages = response.xpath("//div[@class='news-pagination']/ul//a/@href")
		# yield from response.follow_all(pages, self.parse)

		next_page = 'https://www.bks.at/news-presse?p_p_id=com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_4rRcEEkoXQ5d&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_4rRcEEkoXQ5d_delta=10&p_r_p_resetCur=false&_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_4rRcEEkoXQ5d_cur='+ str(self.page_number) +''
		if self.page_number <= 19:
			self.page_number +=1
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		title = response.xpath('//div[@class="content-large"]/h1//text()').getall()
		title = ' '.join(title).strip()
		content = response.xpath('//div[@class="portlet-boundary portlet-bordered portlet-journal-content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))
		date = response.xpath('//div[@class="content-large"]/p[1]//text()').get()

		item = ItemLoader(item=BksItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
