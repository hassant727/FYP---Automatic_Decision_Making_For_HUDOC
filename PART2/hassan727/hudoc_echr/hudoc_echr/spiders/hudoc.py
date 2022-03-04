import csv
import re

import scrapy
from scrapy import Request, Selector


class HudocSpider(scrapy.Spider):
    name = 'hudoc'
    custom_settings = {

        'FEED_URI': f'hudoc_outpu_New.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }
    main_url = "https://hudoc.echr.coe.int/app/conversion/docx/html/body?library=ECHR&id={}"
    headers = {
        'authority': 'hudoc.echr.coe.int',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'accept': 'text/html, */*; q=0.01',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://hudoc.echr.coe.int/eng',
        'accept-language': 'en-US,en;q=0.9',
    }

    def start_requests(self):
        for input_code in self.get_search_criteria_from_file():
            page_code = input_code.get('codes')
            language = input_code.get('language')
            doc_name = input_code.get('doc_name')
            yield Request(
                url=self.main_url.format(page_code),
                callback=self.parse,
                headers=self.headers,
                meta={'language': language, 'doc_name': doc_name}
            )

    def parse(self, response):
        relevent = (''.join(self.extract_text_nodes(
            response.xpath('//span[contains(text(), "RELEVANT LEGAL FRAMEWORK")]/following::p[1]')))).replace('\'',
                                                                                                              '').replace(
            '\"', '').replace(':', '').replace(';', '') + (''.join(self.extract_text_nodes(
            response.xpath('//span[contains(text(), "RELEVANT LEGAL FRAMEWORK")]/following::p[2]')))).replace('\'',
                                                                                                              '').replace(
            '\"', '').replace(':', '').replace(';', '') + (''.join(self.extract_text_nodes(
            response.xpath('//span[contains(text(), "RELEVANT LEGAL FRAMEWORK")]/following::p[3]')))).replace('\'',
                                                                                                              '').replace(
            '\"', '').replace(':', '').replace(';', '') + (''.join(self.extract_text_nodes(
            response.xpath('//span[contains(text(), "RELEVANT LEGAL FRAMEWORK")]/following::p[4]')))).replace('\'',
                                                                                                              '').replace(
            '\"', '').replace(':', '').replace(';', '')
        yield {
            'page_url': response.url,
            'language': response.meta['language'],
            'Case Title': response.meta['doc_name'],
            'JUDGMENT': (
                ''.join(self.extract_text_nodes(response.css('.sE1D97FD,.s89A6D633,.s793ACBC3,.sBEB558E7')))).replace(
                '\'', '').replace('\"', '').replace(':', '').replace(';', ''),
            'introduction': (''.join(self.extract_text_nodes(
                response.xpath('//span[contains(text(), "INTRODUCTION")]/following::p[1]')))).replace('\'', '').replace(
                '\"', '').replace(':', '').replace(';', ''),
            'facts': (''.join(self.extract_text_nodes(
                response.xpath('//span[contains(text(), "THE FACTS")]/following::p[1]')))).replace('\'', '').replace(
                '\"', '').replace(':', '').replace(';', ''),
        
            'conclusion': (''.join(self.extract_text_nodes(
                response.xpath('//span[contains(text(), "Conclusion(s)")]/following::p[1]')))).replace('\'',                                                                                          '').replace('\"',                                                                                                   '').replace(
                ':', '').replace(';', ''),
            'Law': (''.join(
                self.extract_text_nodes(response.xpath('//span[contains(text(), "THE LAW")]/following::p')))).replace(
                '\'', '').replace('\"', '').replace(':', '').replace(';', ''),
            'RELEVANT LEGAL FRAMEWORK': relevent,
            # 'all text': '\n'.join(self.extract_text_nodes(response.xpath('//span[contains(text(), "STRASBOURG")]/following::p')))
        }

    def extract_text_nodes(self, selector, dont_skip=None):
        dont_skip = dont_skip or []
        assert isinstance(dont_skip, list), "'dont_skip' must be a 'list' or None type"

        required_tags = ['p', 'i', 'u', 'strong', 'b', 'em', 'span', 'sup', 'sub', 'font', 'ol', 'li', 'a']
        required_tags.extend(dont_skip)

        texts = selector.extract()
        if not type(texts) is list:
            texts = [texts]
        results = []
        for text in texts:
            for tag in required_tags:
                text = re.sub(r'<\s*%s>' % tag, '', text)
                text = re.sub(r'</\s*%s>' % tag, '', text)
                text = re.sub(r'<\s*%s[^\w][^>]*>' % tag, '', text)
                text = re.sub(r'</\s*%s[^\w]\s*>' % tag, '', text)

            text = text.replace('\r\n', ' ')
            text = re.sub(r'<!--.*?-->', '', text, re.S)
            sel = Selector(text=text)

            # extract all texts except tabular texts
            all_texts = sel.xpath(''.join([
                'descendant::text()/parent::*[name()!="td"]',
                '[name()!="script"][name()!="style"]/text()'
            ])).extract()
            all_texts = map(lambda x: x.strip(), all_texts)
            results += all_texts

        results = [
            text.replace(';', '').replace(':', '').replace('&', '').replace(',', '').replace('\'', '').replace('\"', '')
            for text in results if text]
        return results

    def get_search_criteria_from_file(self):
        with open(file='hudoc_input_new.csv', mode='r') as input_file:
            return list(csv.DictReader(input_file))
