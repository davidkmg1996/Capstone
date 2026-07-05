import scrapy
from scrapy.crawler import CrawlerProcess

class MySpider(scrapy.Spider):
    name = "plantTravel"
    start_urls=["https://www.apsnet.org/edcenter/resources/commonnames/Pages/default.aspx"]
    
    
    def parse(self, response):
        word = "Diseases"
        links_xpath = f"//a[starts-with(normalize-space(.), '{word}')]/@href"
        
        for href in response.xpath(links_xpath).getall():
                 
            yield response.follow(href, callback = self.parseWord)
            
    def parseWord(self, response):
        self.logger.info(f"Scraping data from {response.url}")
        
      #  yield {
      #      'url': response.url,
      #      'title': response.css('title::text').get(),
      #  }
        yield from self.parseDiseasePage(response)
    
    def doNotParse(self, response):
        pass
    def parseDiseasePage(self, response):
        title=response.css("title::text").get(default="")
        plant=title.replace("Diseases of", "").strip() if "Diseases of" in title else title.strip()
        for h3 in response.css("h3"):
            category=h3.css("::text").get(default="").strip()
            dl=h3.xpath("following-sibling::dl[1]")
            for dt in dl.css("dt"):
                disease_name = dt.css("::text").get(default="").strip()
                if not disease_name:
                    continue
                yield {
                    "plant": plant,
                    "category": category,
                    "disease": disease_name,
                }
    
if __name__=="__main__":
    process = CrawlerProcess(
        settings={
            # Output data to JSON file
            "FEEDS": {
                "plant_diseases.json": {"format": "json", "encoding": "utf8"}
            },
            "LOG_LEVEL": "INFO",
        }
    )
    process.crawl(MySpider)
    process.start()
    