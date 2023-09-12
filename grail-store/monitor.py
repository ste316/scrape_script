from mainLib import lib
from scrape import productScraper, mainPageScraper

class monitor():
    def __init__(self, timeout: int) -> None:
        lib.logConsole('Starting...')
        self.proxies = lib.load_proxy()
        if not self.proxies:
            self.proxies = []

        self.timeout = timeout

    def monitorProductPage(self, link: str, send_webhook: bool = False):
        from time import sleep
        scraper = productScraper(self.proxies, True) # pass proxies and suppress info log

        while True:
            res = scraper.scrapeProductPage(link) 
            if res != False: 
                if len(res['sizes']) > 0: # if there is at least 1 size
                    lib.logConsole(f'Product instock - {res["title"]}')
                    if send_webhook: lib.printWebhook(res['sizes'], res['title'], link, res['atc_links'], res['load_links'])
                else: # product Out Of Stock
                    lib.logConsole(f'Product oos - {res["title"]}')
            else: 
                lib.logConsole('Product not loaded')
            sleep(self.timeout)

    def monitorMainPage(self, link:str):
        lib.logConsoleError('Unimplemented function exiting...')
        exit()
        scraper = mainPageScraper(link, self.proxies)

        while True:
            res = lib.retrivePage(link, self.proxies)
            soup = lib.genSoup(res)
            scraper.retriveAtag(soup)
            #print(productScraper.getSku(soup))

if __name__ == '__main__':
    m = monitor(timeout=10)
    link = 'https://www.grail-store.com/en/new-balance-m2002rdn-dark-moss.html'
    m.monitorProductPage(link, send_webhook=True)
