from requests import Session
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

    def checkIfCartable(self, link: str):
        res = self.sess.get(link)
        atc = re.compile("Aggiungi al carrello")
        buy = re.compile("Acquista ora")
        if (type(re.search(atc, str(res.content))) or type(re.search(buy, str(res.content))))  == re.Match:
            soup = BeautifulSoup(res.content, features='lxml')
            result = soup.find_all("div", {"id": "dropdown-options-container_-1"})
            #print(result)
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

    def printWebhook(self, links:list, linksInfo: dict, reqError: bool): # https://discordpy.readthedocs.io/en/latest/api.html
        if len(links) == 0 and reqError:
            embed = DiscordEmbed(title='Unable to scrape, check console', color = 0XFF0000)
        else:
            embed = DiscordEmbed(title='New Product(s) Found', color = 4437377)
            for i in range(len(links)):
                embed.add_embed_field(name=f'', value = f'[**Product {i+1} {"CARTABLE" if linksInfo[links[i]] else "LOADED"}**]({links[i]})', inline = False) # [{links[i]}]

            embed.set_footer(text = f"Monitor by ste#7981", icon_url = self.settings['discord_iconurl'])
            
        self.webhook.add_embed(embed)
        self.webhook.execute()

    def run(self, dumpNewLink: bool):
        try:
            while True:
                newLink = set()
                newLinkInfo = dict()
                res = self.sess.get(self.url_sitemap, params=random.choice(self.param))
                
                if res.status_code != 200:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Error {res.status_code}: page not reached, retriyng...")
                    self.errCount +=1
                    if self.errCount >= 3:
                        self.printWebhook([],[], True)
                    continue
                soup = BeautifulSoup(res.text, features='lxml')
                result = soup.findAll('loc')

                for i in range(len(result)):
                    if result[i].text not in self.urls:
                        self.urls.add(result[i].text)
                        newLink.add(result[i].text)
                        isCartable = self.checkIfCartable(result[i].text)
                        newLinkInfo[str(result[i].text)] = isCartable
                        print(f'[{datetime.now().strftime("%H:%M:%S:%f")}] {result[i].text} {"CARTABLE" if isCartable else ""}')
                        
                if len(newLink) > 0:
                    self.printWebhook(list(newLink), newLinkInfo, False)
                    if dumpNewLink:
                        util.dumpCachedLink(self.urls)
                time.sleep(self.timeout)
        except KeyboardInterrupt:
            print('^C detected, exiting')


if __name__ == '__main__':
    '''
        TODO rewrite this module in Rust
    '''
    main = WSLscraper(3, True)
    main.run(True)

'''
1:
    scrape https://www.withoutstupidlabel.it/
    if <a> data-testid="linkElement" 
        while True:
            bypass queue/question 
                if <a> data-testid="linkElement" href != "https://www.withoutstupidlabel.it"
                    get the link
                    open it and check if it's a product page
                    otherwise continue
        
        checkIfCartable()

'''


# https://www.withoutstupidlabel.it/sitemap.xml
# https://www.withoutstupidlabel.it/cart-page
# https://www.withoutstupidlabel.it/checkout?appSectionParams=