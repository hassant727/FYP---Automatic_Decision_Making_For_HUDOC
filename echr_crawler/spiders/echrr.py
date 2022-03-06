import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import time
import os


def clean_element(s, word):
    str = []
    i = 0
    while i < len(s):
        if s[i].find(word) == -1:
            str.append(s[i])
            i += 1
        else:
            break
    return str


class EchrrSpider(scrapy.Spider):
    name = 'echrr'
    allowed_domains = ['hudoc.echr.coe.int']
    start_urls = ['https://hudoc.echr.coe.int/eng/']

    def __init__(self):
        self.options = Options()
        #comment out if you want selenium to run on screen.
        # self.options.add_argument("headless")
        
        PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")
        #/Users/hassantariq/Downloads/echr/echr/spiders/chromedriver
        self.options.add_experimental_option(
            "excludeSwitches", ["enable-logging"])
        #change the user agent if the page doesnt load.
        self.options.add_argument(
            "user-agent= Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4716.39 Safari/537.36")

        self.driver = webdriver.Chrome(executable_path=r'/Users/hassantariq/Desktop/ECHR_FYP/chromedriver', options=self.options)
        self.driver.set_window_size(1520, 1080)
        self.driver.get(self.start_urls[0])
        time.sleep(4)

        #change the number on the range, to keep scrolling as much as you want, (20 results) per scroll.
        for i in range(5000): # change this number to whatever and it will keep scrolling down
            self.driver.execute_script(
                "window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(1)
        self.html = self.driver.page_source

    def parse(self, response):
        abso_url = 'https://hudoc.echr.coe.int'
        response = Selector(text=self.html)

        links = response.xpath(
            "//div[@class='results-list-block ']//div[@class='headlineContaniner']//a//@href").extract()
        languages = response.xpath(
            "//span[@class='column availableOnlyColumn ']//a//text()").extract()
        i = len(links)
        x = 0
        for link in links:
            if x < i:
                language = languages[x]
                x += 1
            urls = f"{abso_url}{link}"
            print(urls, 'url in paaaarseee')
            yield scrapy.Request(urls, callback=self.parse_2,
             meta={"url": urls,
              "language": language
              }, dont_filter=True
                                 )

    def parse_2(self, response):
        abso_url = 'https://hudoc.echr.coe.int'
        self.driver.get(response.meta['url'])
        self.driver.refresh()
        time.sleep(3)
        resp = self.driver.page_source
        res = Selector(text=resp)

        title_2 = res.xpath("//span[contains(text(), 'CASE')]//following::span//descendant::text()").extract() or None
        
        if title_2 is None:
            time.sleep(3)
            links = res.xpath(
                "//div[@class='languageEntry']//@href").extract()
            for link in links:
                urls = f"{abso_url}{link}"
                print(urls, 'url in paaaarseee')
                yield scrapy.Request(urls, callback=self.parse_links,
                meta={"url": urls, "language":response.meta['language']}, dont_filter=True)
        else:
            title_1 = "CASE OF "
            title_2 = res.xpath("//span[contains(text(), 'CASE')]//following::span//descendant::text()").extract()
            title_2_clean = [el.replace('\xa0', ' ') for el in clean_element(title_2, 'JUDGMENT')]
            clean_title = ' '.join(title_2_clean)

            introduction = res.xpath(
                "//span[contains(text(), 'INTRODUCTION')]//following::span//descendant::text()").extract()
            clean_intro = [el.replace('\xa0', ' ') for el in clean_element(introduction, 'THE FACTS')]

            factt = res.xpath(
                "//span[contains(text(), 'THE FACTS')]//following::span//descendant::text()").extract()
            clean_fact = [el.replace('\xa0', ' ') for el in clean_element(factt, 'RELEVANT LEGAL')]

            unanimous_decision = res.xpath(
                "//span[contains(text(), 'FOR THESE')]//following::span//descendant::text()").extract()
            final_unaimous = [el.replace('\xa0', ' ') for el in clean_element(unanimous_decision, 'Done')]

            
            judgment = res.xpath("//span[contains(text(), 'JUD')]//following::span//descendant::text()").extract()
            clean_judgment = [el.replace('\xa0', ' ') for el in clean_element(judgment, 'STRASBOURG')]

            the_law = res.xpath(
                "//span[contains(text(), 'THE LAW')]//following::span//descendant::text()").extract()
            clean_the_law = [el.replace('\xa0', ' ') for el in clean_element(the_law, 'The parties')]

            relevant_legal = res.xpath("//span[contains(text(), 'RELEVANT LEGAL')]//following::span//descendant::text()").extract()
            relevant_clean= [el.replace('\xa0', ' ') for el in clean_element(relevant_legal,'THE LAW')]
            language = self.driver.find_element_by_xpath("//*[@id='translation']/a/div[2]").click()
            time.sleep(2)
            resp = self.driver.page_source
            res = Selector(text=resp)

            language_1 = res.xpath("//*[@id='officialLanguageTranslationLinks']/div/div/a/div/span//text()").extract_first()

            if (language_1 in ['French', 'Armenian', 'Turkish', 'Russian', 'Italian', 'Serbian', 'Romanian', 'Ukrainian', 'Bulgarian']) :
                yield {
                    "language": response.meta['language'],
                    }
            else :
                yield {
                    "url": response.meta['url'],
                    "language": language_1,
                    "title": (title_1 + clean_title),
                    "JUDGMENT":clean_judgment,
                    "introduction":clean_intro,
                    "Facts": clean_fact,
                    "The Law": clean_the_law,
                    "releavent legal framework": relevant_clean,
                    "Unanimously": final_unaimous
                }
            

    def parse_links(self, response):
        self.driver.get(response.meta['url'])
        self.driver.refresh()
        time.sleep(3)
        for i in range(2):
            time.sleep(1)
            self.driver.execute_script(
                    "window.scrollTo(0,document.body.scrollHeight)")
        resp = self.driver.page_source
        res = Selector(text=resp)

        title_1 = "CASE OF "
        title_2 = res.xpath("//span[contains(text(), 'CASE')]//following::span//descendant::text()").extract()
        title_2_clean = [el.replace('\xa0', ' ') for el in clean_element(title_2, 'JUDGMENT')]
        clean_title = ' '.join(title_2_clean)

        introduction = res.xpath(
            "//span[contains(text(), 'INTRODUCTION')]//following::span//descendant::text()").extract()
        clean_intro = [el.replace('\xa0', ' ') for el in clean_element(introduction, 'THE FACTS')]

        factt = res.xpath(
            "//span[contains(text(), 'THE FACTS')]//following::span//descendant::text()").extract()
        clean_fact = [el.replace('\xa0', ' ') for el in clean_element(factt, 'RELEVANT LEGAL')]

        unanimous_decision = res.xpath(
            "//span[contains(text(), 'FOR THESE')]//following::span//descendant::text()").extract()
        final_unaimous = [el.replace('\xa0', ' ') for el in clean_element(unanimous_decision, 'Done')]

        
        judgment = res.xpath("//span[contains(text(), 'JUD')]//following::span//descendant::text()").extract()
        clean_judgment = [el.replace('\xa0', ' ') for el in clean_element(judgment, 'STRASBOURG')]

        the_law = res.xpath(
            "//span[contains(text(), 'THE LAW')]//following::span//descendant::text()").extract()
        clean_the_law = [el.replace('\xa0', ' ') for el in clean_element(the_law, 'The parties')]

        relevant_legal = res.xpath("//span[contains(text(), 'RELEVANT LEGAL')]//following::span//descendant::text()").extract()
        relevant_clean= [el.replace('\xa0', ' ') for el in clean_element(relevant_legal,'THE LAW')]

        language = self.driver.find_element_by_xpath("//*[@id='translation']/a/div[2]").click()
        time.sleep(2)
        resp = self.driver.page_source
        res = Selector(text=resp)

        language_1 = res.xpath("//*[@id='officialLanguageTranslationLinks']/div/div/a/div/span//text()").extract_first()
        if (language_1 in ['French', 'Armenian', 'Turkish', 'Russian', 'Italian', 'Serbian', 'Romanian', 'Ukrainian', 'Bulgarian']) :
            yield {
                "language": response.meta['language'],
                }
        else :
            yield {
                "url": response.meta['url'],
                "language": language_1,
                "title": (title_1 + clean_title),
                "JUDGMENT":clean_judgment,
                "introduction":clean_intro,
                "Facts": clean_fact,
                "The Law": clean_the_law,
                "releavent legal framework": relevant_clean,
                "Unanimously": final_unaimous
            }
