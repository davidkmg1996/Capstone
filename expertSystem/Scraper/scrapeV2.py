import scrapy
from scrapy.crawler import CrawlerProcess
import requests


class MySpider(scrapy.Spider):
    name = "plantTravel"
    start_urls=["https://plantvillage.psu.edu/plants"]
    link_count = 0
    plant_count = 0

    def parse(self, response):
        url = "https://plantvillage.psu.edu/plants"  
  
        links = response.css('div.topics_item a[href$="/infos"]::attr(href)').getall()
        unique_links = list(set(links))
        
        for link in unique_links:
            url = response.urljoin(link)
            self.link_count+=1
            yield scrapy.Request(url, callback=self.parsePage)

            print("\n\n\n")
        print("links: ",self.link_count)
        print(links)


    def parsePage(self, response):
        plant_name = response.css("h1 span::text").get()
        if isinstance(plant_name, str):
            self.plant_count+=1
        print(plant_name)
        containers =response.xpath('//div[@style="padding-bottom:30px;"]')
        for block in containers:
            disease_headers = block.xpath('.//h4')
            for h4 in disease_headers:
                text = h4.xpath('normalize-space(text())').get(default="")

                if "category" in text.lower():
                    condition=text
                else:
                    disease_name = h4.xpath('normalize-space(text())').get(default="")

                    symptoms = h4.xpath('./following-sibling::div[@class="symptoms"][1]/text()').get(default="").strip()

                    cause = h4.xpath('./following-sibling::div[@class="cause"][1]/text()').get(default="").strip()

                    comments = h4.xpath('./following-sibling::div[@class="comments"][1]/text()').get(default="").strip()

                    management = h4.xpath('./following-sibling::div[@class="management"][1]/text()').get(default="").strip()

                    if  not disease_name=="" and not symptoms=="" and not cause=="" and not management=="" and not condition=="":

                        yield {
                            'plant': plant_name,
                            'type': cause,
                            'disease': disease_name,
                            'symptoms': symptoms,
                            'condition': condition,
                            'comments': comments,
                            'management':management
                            }

    def closed(self, reason):
        print("\n===== FINAL TOTALS =====")
        print("Total links:", self.link_count)
        print("Total plants:", self.plant_count)

if __name__=="__main__":
    process = CrawlerProcess(
        settings={
            # Output data to JSON file
            "FEEDS": {
                "ScrapeOutput.json": {"format": "json", "encoding": "utf8"}
            },
            "LOG_LEVEL": "INFO",
        }
    )
    process.crawl(MySpider)
    process.start()
    