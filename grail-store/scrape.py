from mainLib import lib
from bs4 import BeautifulSoup as bs

class productScraper():
    def __init__(self) -> None:
        pass

    def clearUrl(self, url: str): # remove everything after '?'
        return url.split('?')[0] 

    def retrieveSizes(self, soup: bs): # retrieve all available sizes
        UL_tag = soup.find('ul', {'id': 'custom-variant-boxes'}) # select html tag ul filled with sizes
        liList = []
        for li in UL_tag.find_all("li", {'class': ''}): 
            # instock items have class = '' | out of stock item have class = 'disabled '
            liList.append(li) # add each size
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
        return soup.find_all('ul', {'class':'list-plain'})[0].find('li').text.replace('SKU: ', '')

    # main function of this class, return: 
    #   load size links, add to cart links, sizes, ids, title and sku of a product
    def scrapeProductPage(self, link, proxies): 
        link = self.clearUrl(link)
        res = lib.retrivePage(link, proxies)

        if res.status_code == 200:
            soup = lib.genSoup(res)
            sku = self.getSku(soup)
            list = self.retrieveSizes(soup)
            (load_links, atc_link, size, id) = self.parseInfo(list)
            title = lib.getTitle(soup)
            return (load_links, atc_link, size, id, title, sku)
        else: return (False)

class mainPageScraper():
    def __init__(self, link: str, proxies) -> None:
        self.link = link
        self.proxies = proxies

    def retriveAtag(self, soup: bs): # only for https://www.grail-store.com/en/footwear/sneakers/
        ul = soup.find('ul', {'class': 'list-collection'}) # https://www.grail-store.com/en/new-arrivals/
        a_tag = []

        for tag in ul:
            a_tag.append(tag.find('a', href=True)['href'])
        
        print(a_tag, len(a_tag))
        return a_tag

    def getPage(self):
        return lib.retrivePage(self.link, self.proxies)

if __name__ == '__main__':

    m = mainPageScraper('https://www.grail-store.com/en/footwear/sneakers/page1.html?limit=72', {}) # max limit is 72, after 72 need paging
    m.retriveAtag(lib.genSoup(m.getPage()))
    '''
    s = productScraper()
    baseL = 'https://www.grail-store.com/en/karhu-fusion-20-jet-black-canyon-sunset.html'
    loadL, atcL, size, id, title_, sku = s.scrapeProductPage(link=baseL, proxies= lib.load_proxy())
    lib.printWebhook(size, title_, baseL, atcL, loadL)
    print(f'Product: {baseL}\n\ttitle: {title_}, product id: {sku}\n\tsize available: {", ".join(size)} \
          \n\tAdd to Cart: {", ".join(atcL)}\n\tLoad size link: {", ".join(loadL)}')
    '''