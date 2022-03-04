import json

import scrapy


class HudocSpider_item_code(scrapy.Spider):
    name = 'item_code'
    main_url = "https://hudoc.echr.coe.int/app/query/results?query=contentsitename%3AECHR%20AND%20(NOT%20(doctype%3DPR%20OR%20doctype%3DHFCOMOLD%20OR%20doctype%3DHECOMOLD))%20AND%20((documentcollectionid%3D%22GRANDCHAMBER%22)%20OR%20(documentcollectionid%3D%22CHAMBER%22))&select=sharepointid,Rank,ECHRRanking,languagenumber,itemid,docname,doctype,application,appno,conclusion,importance,originatingbody,typedescription,kpdate,kpdateAsText,documentcollectionid,documentcollectionid2,languageisocode,extractedappno,isplaceholder,doctypebranch,respondent,advopidentifier,advopstatus,ecli,appnoparts,sclappnos&sort=&start={}&length=100&rankingModelId=11111111-0000-0000-0000-000000000000"

    custom_settings = {

        'FEED_URI': f'hudoc_input_new.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': '51189d24f5ca4a0e8078724e965d2f8b',  # '211b5b562ed74c76b780721cbbd84442',

        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'CONCURRENT_REQUESTS': 32,
        'DOWNLOAD_DELAY': 2
    }

    def start_requests(self):
        for i in range(20, 65600, 100):
            yield scrapy.Request(self.main_url.format(str(i)), callback=self.parse)
        # yield scrapy.Request(self.main_url.format(str(20)), callback=self.parse)

    def parse(self, response, **kwargs):
        my_json = json.loads(response.text)['results']
        print("Here is the print --->", len(my_json))
        if my_json:
            for i in my_json:
                item_id = i['columns']['itemid']
                doc_name = i['columns']['docname']
                doc_language = i['columns']['languageisocode']
                yield {
                    'codes': item_id,
                    'language': doc_language,
                    'doc_name': doc_name
                }
