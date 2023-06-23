from types import NoneType
from mainLib import lib
from bs4 import BeautifulSoup as bs
from re import findall
from math import trunc 

class productScraper():
    def __init__(self, proxies: dict) -> None:
        lib.logConsole('[ProductScraper] Starting...')
        self.proxies = proxies

    def clearUrl(self, url: str): # remove everything after '?'
        return url.split('?')[0] 

    def retrieveSizes(self, soup: bs): # retrieve all available sizes
        UL_tag = soup.find('ul', {'id': 'custom-variant-boxes'}) # select html tag ul filled with sizes
        if type(UL_tag) == NoneType:
            return ['One Size', soup.find('form', {'id': 'product_configure_form'})['action']]
        
        liList = []
        for li in UL_tag.find_all('li', {'class': 'active'}):
            liList.append(li)
        
        for li in UL_tag.find_all("li", {'class': ''}): 
            # instock items have class = '' | out of stock item have class = 'disabled '
            liList.append(li) # add each size tag

        return liList

    def genAtcLink(self, id: list): # generate add to cart link for each id
        links = []
        baseLink = 'https://www.grail-store.com/en/cart/add/'
        for i in id:
            links.append(f'{baseLink}{i}/') # concatenate base add to cart link with product, size specif id 
        return links # list of size specif add to cart links 
    
    def parseInfo(self, liList: list): # parse product info: load size links, add to cart links, sizes and ids
        load_link = []
        size = []
        id = []

        # retrive load link, size and ID
        for tag in liList:
            load_link.append(tag.find('a')['href'])
            size.append(tag.find('a').text.strip())
            id.append(tag.find('a')['href'].split('?id=')[1])

        # gen atc link
        atc = self.genAtcLink(id)
        return (load_link, atc, size, id)

    def getSku(self, soup: bs): # get manufacturer product id
        sku = soup.find_all('ul', {'class':'list-plain'})
        if len(sku) == 0: return ''
        return soup.find_all('ul', {'class':'list-plain'})[0].find('li').text.replace('SKU: ', '')

    # main function of this class, return: 
    #   load size links, add to cart links, sizes, ids, title and sku of a product
    def scrapeProductPage(self, link): 
        link = self.clearUrl(link)
        lib.logConsole('[ProductScraper] Scraping next product page...')
        res = lib.retrivePage(link, self.proxies)

        if res.status_code == 200:
            soup = lib.genSoup(res)
            sku = self.getSku(soup)
            list = self.retrieveSizes(soup)
            if len(list) == 2 and list[0] == 'One Size':
                id = [list[1].split('add/')[1].replace('/', '')]
                load_links = [link+'?id='+id[0]]
                atc_links = [list[1]]
                sizes = [list[0]]
            
            else: 
                (load_links, atc_links, sizes, id) = self.parseInfo(list)

            title = lib.getTitle(soup)
            return (load_links, atc_links, sizes, id, title, sku)
        else: return (False)
    
    def printProductInfo(self, print_webhook: bool, load_links: list, atc_links: list, sizes: list, title: str, sku: str, base_link :str):
        if print_webhook: lib.printWebhook(sizes, title, base_link, atc_links, load_links)
        print(f'Product: {base_link}\n\ttitle: {title}\n\tproduct id: {sku}\n\tsize available: {", ".join(sizes)} \
          \n\tAdd to Cart: {", ".join(atc_links)}\n\tLoad size link: {", ".join(load_links)}')

class mainPageScraper():
    def __init__(self, link: str, proxies) -> None:
        lib.logConsole(f'[MainPageScraper] Starting...')
        self.link = link
        self.proxies = proxies

    def getLinksWithPaging(self):
        itemPerPage = 72 # 72 is the maximum option available, the higher this number, the fewer pages to get(request) -> the shorter the execution time
        res = self.getPage()
        soup = lib.genSoup(res)

        lib.logConsole(f'[MainPageScraper] Getting pages...')
        try: 
            # find total number of product, divide it per itemPerPage, take the whole part and sum 1
            # to get the correct number of pages
            numberOfAllProd = int(findall(r'\d+', soup.find('h5', {'class': 'mobile-hide'}).text)[0]) # regex findall
            numberOfPage = trunc(numberOfAllProd / itemPerPage)+1 
        except Exception as e:
            print(f'error while gtting paging: {e}')
            exit()

        linkPaging = [f'{self.link}page{i}.html?limit={itemPerPage}' for i in range(1, numberOfPage+1)] # build links
        return linkPaging

    def retriveAtag(self, link): # retrieve all product links in the page
        # works for https://www.grail-store.com/en/footwear/sneakers/  https://www.grail-store.com/en/new/ ecc
        res = lib.retrivePage(link, self.proxies)
        soup = lib.genSoup(res)

        ul = soup.find('ul', {'class': 'list-collection'}) 
        return [tag.find('a', href=True)['href'] for tag in ul] 

    def getPage(self):
        return lib.retrivePage(self.link, self.proxies)

    def getAllProductsLinks(self):
        links = self.getLinksWithPaging()
        pd_link = set() # to avoid eventual duplicated link

        lib.logConsole(f'[MainPageScraper] Retriving product links...')
        for link in links:
            pd_link.update(set(self.retriveAtag(link)))

        lib.logConsole(f'[MainPageScraper] found {len(pd_link)} products')
        return list(pd_link)

if __name__ == '__main__':
    
    m = mainPageScraper('https://www.grail-store.com/en/new/', {}) # max limit is 72, after 72 need paging
    all = m.getAllProductsLinks()

    s = productScraper({})
    for baseL in all:
        load_links, atc_links, sizes, id, title, sku = s.scrapeProductPage(link=baseL)
        # s.printProductInfo(False, load_links, atc_links, sizes, title, sku, baseL)

    '''
    s = productScraper(proxies=lib.load_proxy())
    a = s.scrapeProductPage('https://www.grail-store.com/en/daily-paper-ralo-shorts.html')
    print(a)
    '''
    
