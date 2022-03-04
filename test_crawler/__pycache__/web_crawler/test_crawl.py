from web_crawler import HUDOC_Crawler

url = "https://ocw.mit.edu"
start_anchor = "/"
urls = HUDOC_Crawler.crawl(url, start_anchor)
print(len(urls))