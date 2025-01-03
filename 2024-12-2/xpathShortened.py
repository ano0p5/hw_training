import requests
from parsel import Selector
import random
import json

class OLXScraper:
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36"
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "User-Agent": random.choice(self.user_agents)  
        })
        self.results = []  
        self.max_results = 500  
        self.page_counter = 0  
        self.json_filename = 'olx.json'

        
        try:
            with open(self.json_filename, 'r', encoding='utf-8') as f:
                self.results = json.load(f)  
        except FileNotFoundError:
            with open(self.json_filename, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)  

    def fetch_page(self, url):
        print(f"Fetching: {url}")  
        response = self.session.get(url)
        if response.status_code == 200:
            return Selector(response.text)
        else:
            print(f"Failed to fetch {url}, Status Code: {response.status_code}")
            return None

    def parse_listing_page(self, url):
        selector = self.fetch_page(url)
        if not selector:
            return

        url_prefix = "https://www.olx.in"

        
        for listing in selector.xpath("//li[contains(@class, '_1DNjI')]"):
            relative_url = listing.css('a::attr(href)').get()  
            if relative_url:
                listing_url = url_prefix + relative_url  
                print(f"Fetching listing: {listing_url}")
                self.parse_listing(listing_url)

                
                if len(self.results) >= self.max_results:
                    print("Reached maximum limit of 1000 listings.")
                    return

        
        next_page_url = selector.css('a._30kbx.da3cR::attr(href)').get()
        if next_page_url and len(self.results) < self.max_results:
            next_page_full_url = url_prefix + next_page_url
            print(f"Going to next page: {next_page_full_url}")
            self.page_counter += 1
            print(f"Fetching Page {self.page_counter}...")
            self.parse_listing_page(next_page_full_url)

    def parse_listing(self, url):
        selector = self.fetch_page(url)
        if not selector:
            return

        data = {
            'property_name': selector.css('h1[data-aut-id="itemTitle"]::text').get(),
            'property_id': selector.xpath("(//div[@class='_1-oS0']//strong)[3]/text()").get(),
            'breadcrumbs': selector.xpath("//ol[@class='rui-2Pidb']//a[@class='_26_tZ']/text()").getall(),
            'price': selector.css('span[data-aut-id="itemPrice"]::text').get(),
            'image_url': selector.css('img[data-aut-id="defaultImg"]::attr(src)').get(),
            'description': selector.css('div[data-aut-id="itemDescriptionContent"] p::text').getall(),
            'seller_name': selector.xpath('//div[@class="eHFQs"]/text()[normalize-space()]').get(),
            'location': selector.xpath('//span[@class="_1RkZP"]/text()').get(),
            'property_type': selector.xpath('//span[@class="B6X7c"]/text()').get(),
            'bathrooms': selector.xpath('//span[@data-aut-id="value_bathrooms"]/text()').get(),
            'bedrooms': selector.xpath('//span[@data-aut-id="value_rooms"]/text()').get(),
        }
  
        self.results.append(data)
        print(data)

        
        with open(self.json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)

    def save_to_json(self):
        with open(self.json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {self.json_filename}")

if __name__ == "__main__":
    scraper = OLXScraper()
    start_url = "https://www.olx.in/kozhikode_g4058877/for-rent-houses-apartments_c1723"
    scraper.parse_listing_page(start_url)

