import scrapy
import datetime
import time
import os
import re
from nekretninespider.items import AdItem



class NekretninetSpider(scrapy.Spider):
    name = "nekretnine_spider"
    #start_urls = ['https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/izdavanje/grad/beograd/lista/po_stranici/50/']
    start_urls = ['https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/izdavanje/grad/beograd/poredjaj-po/datumu_nanize/lista/po_stranici/50/']
    number_of_pages = 0
    number_of_pictures = 0
    items_counter = 0
    FILE_LAST_SCRAPED = 'last_items.csv'
    FILE_ALL_ITEMS = 'all_items.csv'
    file_all_items = scrapy.Field()
    last_scraped_item = AdItem()
    stop_scraping = False
    new_items_list = []

    def start_requests(self):
        self.last_scraped_item = self.get_last_scraped_item()
        self.open_all_items_file()
        yield scrapy.Request(self.start_urls[0], self.parse)

    def parse(self, response):
        if self.number_of_pages < 1:
            self.number_of_pages = self.number_of_pages + 1

            # selectors
            list_result_selector = '.resultList'
            name_selector = 'h2 a ::text'
            location_selector = './/div[2]/div[1]/text()'
            price_selector = './/div[2]/div[2]/text()'
            link_selector = 'h2 a ::attr(href)'

            for listResult in response.css(list_result_selector):
                self.items_counter = self.items_counter + 1
                item = AdItem()
                item['id'] = self.items_counter
                item['name'] = listResult.css(name_selector).extract_first()
                item['location'] = listResult.xpath(location_selector).extract_first()
                item['price'] = listResult.xpath(price_selector).extract_first()
                item['link'] = listResult.css(link_selector).extract_first()

                if item['link']:
                    if item['link'] != self.last_scraped_item['link']:
                        yield scrapy.Request(url=item['link'], callback=self.parse_details, meta={'item': item})
                    else:
                        self.stop_scraping = True
                        break

            if not self.stop_scraping:
                next_page_selector = '.pag_next ::attr(href)'
                next_page = response.css(next_page_selector).extract_first()
                if next_page:
                    yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_details(self, response):
        item = response.meta['item']
        image_counter = 0
        file_paths = []
        file_urls = []

        #selectors
        updated_selector = '.sLeftGrid > ul:nth-child(2) > li:nth-child(3) > div:nth-child(2) ::text'
        image_selector = '#a' + str(image_counter) + ' > img'

        item['updated'] = response.css(updated_selector).extract_first()
        if bool(re.compile('\n').search(item['updated'])):
            item['updated'] = ''
        image_tag = response.css(image_selector)
        while image_tag:
            path = image_tag.xpath("@src").extract_first()
            file_paths.append(path)
            file_urls.append(response.urljoin(path))
            image_counter = image_counter + 1
            image_selector = '#a' + str(image_counter) + ' > img'
            image_tag = response.css(image_selector)
        item['file_paths'] = file_paths
        item['file_urls'] = file_urls
        self.new_items_list.append(item)
        return item

    def close(self, spider):
        if len(self.new_items_list) > 0:
            new_items_sorted_list = sorted(self.new_items_list, key=self.getKey)
            self.save_items(new_items_sorted_list)
        self.close_all_items_file()

    def getKey(self, item):
        return item['id']

    def save_items(self, items_list):
        for item in items_list:
            st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
            self.file_all_items.write(st + '\t' + item['name'] + '\t' + item['location'] + '\t' + item['price'] + '\t' +
                                  str(len(item['file_paths'])) + '\t' + item['link'] + '\t' + item['updated'] + '\n')
            self.file_all_items.flush()
        if items_list[0]:
            self.update_last_scraped_item(items_list[0])

    def update_last_scraped_item(self, item):
        file_last_scraped = open(self.FILE_LAST_SCRAPED, 'w+')
        file_last_scraped.write(item['name'] + '\t' + item['location'] + '\t'
                                + item['price'] + '\t'
                                + str(len(item['file_paths']))
                                + '\t' + item['link'] + '\t'
                                + item['updated'] + '\n')
        file_last_scraped.close()

    def get_last_scraped_item(self):
        last_scraped_item = AdItem()
        last_scraped_item['link'] = ''
        if os.path.exists(self.FILE_LAST_SCRAPED):
            file_last_scraped = open(self.FILE_LAST_SCRAPED, 'r')
            splited_item = file_last_scraped.readline().split('\t')
            if len(splited_item) > 5:
                last_scraped_item['link'] = splited_item[4]
                #self.last_scraped_item['updated'] = splited_item[5] if dim > 5 else ''
            file_last_scraped.close()
        print('Last scraped item: ' + last_scraped_item['link'])
        return last_scraped_item

    def open_all_items_file(self):
        if os.path.exists(self.FILE_ALL_ITEMS):
            append_write = 'a'
        else:
            append_write = 'w'
        self.file_all_items = open(self.FILE_ALL_ITEMS, append_write)

    def close_all_items_file(self):
        if hasattr(self, 'closed') and not self.closed:
            self.file_all_items.close()