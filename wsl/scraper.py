from requests import Session, Response
from datetime import datetime
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from discord_webhook import DiscordEmbed
import random
import time
import re
from lib1 import util
from warnings import filterwarnings

filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

class WSLscraper():
    def __init__(self, timeout, loadCachedLink: bool) -> None:
        self.settings = util.loadSettings()
        self.url_sitemap = 'https://www.withoutstupidlabel.it/store-products-sitemap.xml'
        self.urls = set()
        self.sess = Session()
        self.sess.proxies = util.loadProxy()
        self.sess.headers['User-Agent'] = util.get_random_agent()
        self.webhook = util.setupWebhook(self.settings['discord_webhook'])
        self.errCount = 0
        self.param = self.genParams()
        self.timeout = timeout
        if loadCachedLink: self.urls.update(util.loadCachedLink())

    def getProductInfo(self, link: str):
        res = self.sess.get(link)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, features='html.parser')

            price, title = '', ''
            isCartable = False
            try:
                #<span data-hook="formatted-primary-price">€ 79,00</span>
                price = soup.find('span', {"data-hook": "formatted-primary-price"}).text
                # <h1 data-hook="product-title" class="_2qrJF igTU-">Basic Tee pack (2pz)</h1>
                title = soup.find('h1', {'data-hook': 'product-title'}).text
                isCartable = self.checkIfCartable(res)
            except:
                pass
            return title, price, isCartable

        else: return False, False, False

    def checkIfCartable(self, res: Response):
        atc = re.compile("Aggiungi al carrello")
        buy = re.compile("Acquista ora")
        if (type(re.search(atc, str(res.content))) or type(re.search(buy, str(res.content)))) == re.Match:
            # soup = BeautifulSoup(res.content, features='lxml')
            # result = soup.find_all("div", {"id": "dropdown-options-container_-1"})
            # print(f'Func checkIfCartable {result=}')
            return True
        return False

    def genParams(self):
        param = list()
        for i in range(100):
            param.append ({
                util.get_random_string(): random.randint(0,10000000),
                util.get_random_string(): random.choice(['true', 'false']),
            })
        return param

    def printWebhook(self, linksInfo: list, reqError: bool): # https://discordpy.readthedocs.io/en/latest/api.html
        if len(linksInfo) == 0 and reqError:
            embed = DiscordEmbed(title='Unable to scrape, check console', color = 0XFF0000)
            self.webhook.add_embed(embed)
            self.webhook.execute()
        else:
            # Split links into chunks of 10
            for i in range(0, len(linksInfo), 10):
                chunk = linksInfo[i:i+10]
                embed = DiscordEmbed(title='New Product(s) Found!', color = 4437377)
                
                for info in chunk:
                    date_str = f" (Added: {info['date']})" if info['date'] else ""
                    value = f'[**{info["title"]}**]({info["link"]}) {"CARTABLE" if info["isCartable"] else "LOADED"} {info["price"]}{date_str}'
                    embed.add_embed_field(name='\u200b', value=value, inline=False)

                embed.set_footer(text = f"Monitor by ste#7981", icon_url = self.settings['discord_iconurl'])
                embed.set_timestamp(int(datetime.now().timestamp()))
                
                self.webhook.add_embed(embed)
                self.webhook.execute()
                self.webhook.embeds.clear()  # Clear embeds for next iteration

    def getSitemap(self) -> Response:
        return self.sess.get(self.url_sitemap, params=random.choice(self.param))

    def getLinkFromXml(self, res: Response):
        soup = BeautifulSoup(res.text, features='lxml')
        urls = soup.findAll('url')
        products = []
        for url in urls:
            products.append({
                'link': url.find('loc').text,
                'date': url.find('lastmod').text if url.find('lastmod') else None
            })
        # Sort by date, newest first
        return sorted(products, key=lambda x: x['date'] or '', reverse=True)

    def run(self, dumpNewLink: bool):
        try:
            while True:
                newLink = []
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Getting main page...")
                res = self.getSitemap()

                if res.status_code != 200:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Error {res.status_code}: page not reached, retriyng...")
                    self.errCount +=1
                    if self.errCount >= 3:
                        self.printWebhook([],[], True)
                    continue
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Successfully got main page...")
                products = self.getLinkFromXml(res)

                print(f"[{datetime.now().strftime('%H:%M:%S')}] Scraping product pages found...")
                for product in products:
                    if product['link'] not in self.urls:
                        for _ in range(3): # try maximum 3 times
                            info = self.getProductInfo(product['link'])
                            if not info[0] and not info[1] and not info[2]:
                                continue
                            break
                        title, price, isCartable = info

                        self.urls.add(product['link'])
                        newLink.append({
                            'link': product['link'],
                            'title': title,
                            'price': price,
                            'isCartable': isCartable,
                            'date': product['date']
                        })
                        print(f'[{datetime.now().strftime("%H:%M:%S")}] New Product Found! {product["link"]}, Date: {product["date"]}, IsCartable: {isCartable}, title: {title}, price: {price}')

                if len(newLink) > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] New product found: {len(newLink)}")
                    self.printWebhook(newLink, False)
                    if dumpNewLink:
                        util.dumpCachedLink(self.urls)
                time.sleep(self.timeout)
        except KeyboardInterrupt:
            print('CTRL C detected, exiting')

if __name__ == '__main__':
    use_cached_link = True
    main = WSLscraper(1, use_cached_link)
    main.run(use_cached_link)
