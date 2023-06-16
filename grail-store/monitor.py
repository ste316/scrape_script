from mainLib import lib
from scrape import productScraper, mainPageScraper
import time

class monitor():
    def __init__(self, timeout: int) -> None:
        lib.logConsole('Starting...')
        self.proxies = lib.load_proxy()
        if not self.proxies:
            self.proxies = []

        self.timeout = timeout

    def monitorProductPage(self, link: str):
        scraper = productScraper()

        while True:
            res = scraper.scrapeProductPage(link, self.proxies)
            if res != False: 
                (load_links, atc_link, size, id, title, sku) = res
                if len(size) > 0:
                    lib.logConsole(f'Product instock - {title}')
                    lib.printWebhook(size, title, link, atc_link, load_links)
                else:
                    lib.logConsole(f'Product oos - {title}')
            else: 
                lib.logConsole('Product not loaded')
            time.sleep(self.timeout)

    def monitorMainPage(self, link:str):
        scraper = mainPageScraper()

        while True:
            res = lib.retrivePage(link, self.proxies)
            soup = lib.genSoup(res)
            scraper.retriveAtag(soup)
            #print(productScraper.getSku(soup))

if __name__ == '__main__':
    m = monitor(timeout=10)
    link = 'https://www.grail-store.com/en/new-balance-550hg1-white-orange.html'
    link = 'https://www.grail-store.com/en/new-balance-uxc72ec-black-grey-ivory.html'
    m.monitorProductPage(link)

    #m.monitorMainPage('https://www.grail-store.com/en/new-arrivals/')
    

# https://www.grail-store.com/en/new-balance-550hg1-white-orange.html
# https://www.grail-store.com/en/new-balance-550hl1-white-light-blue.html
