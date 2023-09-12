from types import NoneType
from mainLib import lib
from bs4 import BeautifulSoup as bs
from re import findall
from math import trunc 
from json import dumps, loads

# This class can scrape Grail Store product pages
# also in bulk by passing a list of links
class productScraper():
    def __init__(self, proxies: dict, suppressInfoLog: bool = False) -> None:
        self.proxies = proxies
        self.suppressInfoLog = suppressInfoLog
        if not self.suppressInfoLog: lib.logConsole('[ProductScraper] Starting...')
    
    # remove everything after '?'
    def clearUrl(self, url: str): 
        return url.split('?')[0] 
    
    # retrieve all available sizes
    def retrieveSizes(self, soup: bs): 
        UL_tag = soup.find('ul', {'id': 'custom-variant-boxes'}) # select html tag 'ul' filled with sizes
        if type(UL_tag) == NoneType:
            # handle One Size product case 
            return ['One Size', soup.find('form', {'id': 'product_configure_form'})['action']]
        
        liList = []
        for li in UL_tag.find_all('li', {'class': 'active'}): # item selected
            liList.append(li)
        
        for li in UL_tag.find_all("li", {'class': ''}): 
            # instock items have class = '' 
            # out of stock item have class = 'disabled '
            liList.append(li) # add each size tag

        return liList

    # generate add to cart link for each id
    def genAtcLink(self, id: list): 
        links = []
        baseLink = 'https://www.grail-store.com/en/cart/add/'
        links = [f'{baseLink}{i}/' for i in id] # concatenate add_to_cart link with size specific product
        return links # list of size specif add to cart links 
    
    # parse product info: load links, add to cart links, sizes and ids
    def parseInfo(self, liList: list):
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

    # get manufacturer product id
    def getSku(self, soup: bs):
        sku = soup.find_all('ul', {'class':'list-plain'})
        if len(sku) == 0: return ''
        return soup.find_all('ul', {'class':'list-plain'})[0].find('li').text.replace('SKU: ', '').replace('EAN: ', '')

    # main function of this class, return: 
    #   load size links, add to cart links, sizes, ids, title and sku of a product
    #   or False if not success
    def scrapeProductPage(self, link: str): 
        link = self.clearUrl(link)
        if not self.suppressInfoLog: lib.logConsole('[ProductScraper] Scraping next product page...')
        res = lib.retrivePage(link, self.proxies)

        if res.status_code == 200:
            soup = lib.genSoup(res)
            sku = self.getSku(soup)
            list = self.retrieveSizes(soup)
            if len(list) == 2 and list[0] == 'One Size': # handle One Size case
                id = [list[1].split('add/')[1].replace('/', '')]
                load_links = [link+'?id='+id[0]]
                atc_links = [list[1]]
                sizes = [list[0]]
            
            else: 
                (load_links, atc_links, sizes, id) = self.parseInfo(list)

            title = lib.getTitle(soup)
            return {
                'title': title,
                'sku': sku if len(sku)>0 else title.replace(' ', ''),
                'id': id,
                'sizes': sizes,
                'load_links': load_links,
                'atc_links': atc_links
            }
        else: 
            lib.logConsoleError(f'Error: status code: {res.status_code}')
            return False
    
    def printProductInfo(self, print_webhook: bool, load_links: list, atc_links: list, sizes: list, title: str, sku: str, base_link :str):
        if print_webhook: lib.printWebhook(sizes, title, base_link, atc_links, load_links)
        if not self.suppressInfoLog: lib.logConsoleProduct(f'Product: {base_link}\n\ttitle: {title}\n\tproduct id: {sku}\n\tsize available: {", ".join(sizes)} ')
        #      \ \n\tAdd to Cart: {", ".join(atc_links)}\n\tLoad size link: {", ".join(load_links)}')

    # usefull function to scrape a list of grail store product all in once
    # you can and it is reccomended to set dump_json as True to get all scraped infos saved
    # you can also have a webhook notification with product infos [not fully implemented yet] 
    def bulkScraping(self, links: list[str], send_webhook: bool = False, dump_json: bool = True):
        
        # dump will produce a json file called data.json
        # inside you will find your scraped product 
        # indexed by SKU provided by the site
        def dump(obj):
            filename = lib.writeFile('data.json', dumps(obj, indent=4))
            lib.logConsole(f'[ProductScraper] You can find all products at {filename}')

        all_product = dict()
        for link in links:
            data = self.scrapeProductPage(link)
            if not data:
                # add error handling :(
                pass
            else:
                sku = data.pop("sku")
                all_product.update({sku: data})
        
        # if send_webhook: call function to send all product to webhook
        if dump_json: dump(all_product)

        return all_product

    def bulkSendWebhook(self, product: list[dict]):
        lib.logConsoleError('Error: Unimplemented function exiting...')
        exit()
        webhook_list = lib.loadJsonFile('settings.json')['discord_webhook_links']
        prdXwebhook = int(len(product) // len(webhook_list))
        rest = int(len(product) % len(webhook_list))
        '''
        TODO
        create a thread for each webhook, split the product between them
        read the response body to see if the webhook were sent otherwise
        sleep the amount of time (is in the respose body)
        '''

# This class can scrape Grail Store pages with list of product
# for example categorie pages such as https://www.grail-store.com/en/footwear/sneakers/  
class mainPageScraper():
    def __init__(self, link: str, proxies) -> None:
        lib.logConsole(f'[MainPageScraper] Starting...', True)
        self.link = link
        self.proxies = proxies

    # return a list of links to perform a get request to self.link
    # it is optimized to get as more products as possible in the same link
    def getLinksWithPaging(self):
        itemPerPage = 72 
        # 72 is the maximum option available, the higher this number, 
        # the fewer pages to get(request) -> the shorter the execution time

        res = lib.retrivePage(self.link, self.proxies)
        soup = lib.genSoup(res)

        lib.logConsole(f'[MainPageScraper] Getting pages...', True)
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
    
    # retrieve all product links in the page
    def retriveAtag(self, link): 
        # works for https://www.grail-store.com/en/footwear/sneakers/  https://www.grail-store.com/en/new/ ecc
        res = lib.retrivePage(link, self.proxies)
        soup = lib.genSoup(res)

        ul = soup.find('ul', {'class': 'list-collection'}) 
        return [tag.find('a', href=True)['href'] for tag in ul] 

    # main function of this class
    def getAllProductsLinks(self):
        links = self.getLinksWithPaging()
        pd_link = set() # to avoid eventual duplicated link

        lib.logConsole(f'[MainPageScraper] Retriving product links...', True)
        for link in links:
            pd_link.update(set(self.retriveAtag(link)))

        lib.logConsole(f'[MainPageScraper] found {len(pd_link)} products', True)
        return list(pd_link)

if __name__ == '__main__':
    # mainPageScraper also works for 
    # https://www.grail-store.com/en/footwear/sneakers/  
    # https://www.grail-store.com/en/new/ 
    # ecc...
    m = mainPageScraper('https://www.grail-store.com/en/new/', {}) # max limit is 72, after 72 need paging
    all = m.getAllProductsLinks()

    s = productScraper({})
    s.bulkScraping(all, dump_json=True)
