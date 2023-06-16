from mainLib import lib
from random import choice
from requests_html import HTMLSession # https://docs.python-requests.org/projects/requests-html/en/latest/
from bs4 import BeautifulSoup as bs

class bot():
    # TODO settare addy, ship, payment, terms uno alla volta
    def __init__(self, atc_link: list, proxies: list = []):
        if len(proxies) > 0:
            self.proxy = choice(proxies)
        else: self.proxy = {}
        # TODO fix proxy loading when no proxy are found
            # TODO modify performRequestBot and performRequest
        
        self.atc = choice(atc_link)
        self.headers = lib.defaultHeader()
        self.s = lib.genSession()

    def performRequestBot(self, s: HTMLSession = '', method: str = 'get', url: str = '', headers: dict = {}, proxy: dict = {}, cookies: dict = {}, json= ''):  
        if headers == {}:
            headers = self.headers
        if proxy == {}:
            proxy = self.proxy
        if s == '':
            s = self.s

        if json == '':
            return lib.performRequest(s=s, method=method, url=url, headers=headers, proxy=proxy, cookies=cookies)
        else: 
            return lib.performRequest(s=s, method=method, url=url, headers=headers, proxy=proxy, cookies=cookies, json=json)

    def cart(self, qta: int):
        res = self.performRequestBot(method='get', url='https://www.grail-store.com/en/')
        res = self.performRequestBot(method='get', url='https://www.grail-store.com/en/cookielaw/optOut/', proxy=self.proxy) #set cookielaw to false
        cartData = {'bundle_id': '', 'matrix_non_exists': '', 'quantity': str(qta)}
        res = self.performRequestBot(method='post', url=self.atc, json=cartData)
        
        if res.status_code == 200:
            cartedItem = self.getCart(lib.genSoup(res))
            lib.logConsole(f'Carted {cartedItem} item')
        else:
            print(res.status_code)

    '''
    def newCheckout(self):
        urlCheck = 'https://www.grail-store.com/en/checkout/onestep/'
        urlAtc = self.atc
        url = 'https://www.grail-store.com/en/'
        browser = start_firefox(url=url, headless=True)
        browser.get(urlAtc)
        browser.get(urlCheck)
        browser.post('https://www.grail-store.com/en/checkout/onestep/details/', data='')
        html = browser.page_source
        open('debug2.html', 'w', encoding="utf-8").write(str(html))
    '''

    def checkout(self):
        lib.logConsole('Proceding to checkout')
        res = self.performRequestBot(method='get', url='https://www.grail-store.com/en/checkout/onestep/')
        req_id = res.headers['cf-ray'].split('-')[0]

        checkoutJS = self.performRequestBot(self.s, method='get', url='https://cdn.webshopapp.com/assets/jquery-1-9-1.js?2021-06-28', headers=self.getJSheader()).text
        res.html.render(retries=3, sleep=4, timeout=10, keep_page=True)
        res.html.render(script=checkoutJS, keep_page=True)

        open('debug.html', 'w', encoding="utf-8").write(str(res.text))


    def getCart(self, soup: bs):
        return soup.find_all('span', {'class': 'no'})[1].text

    def getJSheader(self):
        return {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "cdn.webshopapp.com",
            "Referer": "https://www.grail-store.com/",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": lib.get_random_agent(),
        }

if __name__ == '__main__':
    b = bot( 
            proxies=[], 
            atc_link=['https://www.grail-store.com/en/cart/add/253429461/'] #, 'https://www.grail-store.com/en/cart/add/253429465/'
        )
    b.cart(qta=1)
    b.checkout()



'''
https://www.grail-store.com/en/cart/add/258574455/
https://www.grail-store.com/en/cart/
https://www.grail-store.com/en/checkout/


https://www.grail-store.com/en/checkout/onestep/?format=json

region = 3696	Object { id: "3696", code: "IT-BI", name: "Biella" }


key = https://www.grail-store.com/en/checkout/onestep/?format=json res json [page] key
request_id = https://cdn.webshopapp.com/assets/checkout/checkout.js?2021-06-28?10

'''
