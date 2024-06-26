from lib import tool

class adidasStockScraper:
    def __init__(self, domain: str, timeout: float = 4, loop_mode: bool = False):
        # to slightly improve performance when a module is only needed in 
        # one function I import it only inside that function
        from requests import Session
        '''
                provide:
                    adidas domain eg. www.adidas.it, www.adidas.de, ecc
                    timeout       e.g. 3 as float for 3 seconds
                    loop mode     e.g. True or False [NOTE at the moment not always working] 
        '''
        self.domain = domain
        self.timeout = abs(timeout)
        self.loop = loop_mode
        self.sess = Session()
        self.sess.headers = self.getHeader()
        self.sess.proxies = self.loadProxy()

    # by passing a Product Id, return an adidas link 
    def getPageOf(self, pid: str) -> str: 
        return f'https://{self.domain}/STE316/{pid}.html'

    # provide a Product Id to get stock info
    def getStockOf(self, pid: str):
        link = f'https://{self.domain}/api/products/{pid}/availability'
        res = self.sess.get(link)
        if res.status_code != 200:
            tool.printFail(f'[{tool.getTime()}] [ERROR] Response code: {res.status_code}')
            return False
        
        if 'Your browser is not supported' in res.text:
            # change user agent
            self.sess = self.getHeader()
            tool.printWarn(f"[{tool.getTime()}] [WARNING] Cannot reach the page, changing User Agent")
            return False

        return res.json()

    # load your proxy
    def loadProxy(self) -> list[str]:
        from re import compile, search, Match
        ipv6 = compile('^(?:(?:[0-9A-Fa-f]{1,4}:){6}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|::(?:[0-9A-Fa-f]{1,4}:){5}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,4}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))|(?:(?:[0-9A-Fa-f]{1,4}:){,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){,6}[0-9A-Fa-f]{1,4})?::)(?:%25(?:[A-Za-z0-9\\-._~]|%[0-9A-Fa-f]{2})+)?$')
        ipv4 = compile('^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$')
        fileProxy = open('proxies.txt', 'r')
        proxyList = []
        valid_ip = 0
        if fileProxy.newlines != '': 
            tool.printWarn(f'[{tool.getTime()}] [INFO] Loading proxy')
            for line in fileProxy:
                tempL = line.strip().split(':')
                if type(search(ipv4,line)) or type(search(ipv6,line)) == Match :
                    proxyList.append({'http':'http://'+tempL[2]+tempL[3]+'@'+tempL[0]+':'+tempL[1]}) ; valid_ip+=1 # proxies with auth --> proxies = {"http": "http://user:pass@ip:port/"}
            tool.printWarn(f'[{tool.getTime()}] [INFO] Found '+str(valid_ip)+' valid ip')
        else: tool.printWarn(f'[{tool.getTime()}] [INFO] Using local ip')
        return proxyList

    # return a Request Header for adidas domains
    def getHeader(self) -> dict[str, str]:
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'DNT': '1', # request to not being tracked by the site
            'Host': self.domain,
            'User-Agent': self.get_random_agent()
        }

    # return a random user agent from a pre defined list
    def get_random_agent(self) -> str:
        from random import choice
        '''
                return a randon user agent
                some user agent might not work in some adidas domain
                due to the fact that they are old versions of some browsers
        '''
        user_agent_list = [ 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36','Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36','Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36','Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36','Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)','Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko','Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)','Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko','Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko','Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko','Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)','Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko','Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',  'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko','Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)','Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)','Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)','Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 YaBrowser/16.11.1.673 Yowser/2.5 Safari/537.36','Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36','Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0','Mozilla/5.0 (Windows NT 6.1; rv:45.0) Gecko/20100101 Firefox/45.0','Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0','Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0','Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 YaBrowser/17.6.0.1633 Yowser/2.5 Safari/537.36','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36 OPR/43.0.2442.806 (Edition Yx)','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 YaBrowser/17.1.0.2034 Yowser/2.5 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 YaBrowser/16.11.1.673 Yowser/2.5 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36','Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 OPR/42.0.2393.94','Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36','Mozilla/5.0 (Linux; Android 6.0; thl T9 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.85 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 6.0.1; SM-G925I Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 6.0.1; Redmi Note 3 Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 5.1; Micromax Q334 Build/LMY47I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 5.0; PowerFive Build/LRX21M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 4.4.4; MFLogin3T Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Safari/537.36','Mozilla/5.0 (Linux; Android 4.4.4; MFLogin3T Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.135 Safari/537.36','Mozilla/5.0 (Linux; Android 4.4.2; TZ707 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Safari/537.36','Mozilla/5.0 (Linux; Android 4.4.2; 9005X Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Safari/537.36','Mozilla/5.0 (Linux; Android 4.1.2; LG-E455 Build/JZO54K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 4.1.2; LG-E455 Build/JZO54K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 YaBrowser/16.10.2.1487.00 Mobile Safari/537.36','Mozilla/5.0 (iPad; CPU OS 5_0_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A405 Safari/7534.48.3','Mozilla/5.0 (Android 5.0; Mobile; rv:38.0) Gecko/20100101 Firefox/38.0','Mozilla/5.0 () AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',]
        return choice(user_agent_list)

    # main function
    def run(self, pids: list) -> None:
        from time import sleep
        while True:
            for pid in pids:
                tool.printWarn(f'[{tool.getTime()}] [INFO] Retriving product {tool.PURPLE}{pid}{tool.ENDC}...')
                res = self.getStockOf(pid)
                if not res:
                    if self.loop:
                        tool.printWarn(f'[{tool.getTime()}] [INFO] Retrying...')
                    else:
                        if pids.index(pid) != len(pids)-1:
                            tool.printWarn(f'[{tool.getTime()}] [INFO] Skipping to next product...')
                    sleep(self.timeout)
                    continue 
                
                # some product are loaded as preview aka stock numbers not available, but probably will be soon
                if res['availability_status'] == 'PREVIEW':
                    tool.printWarn(f"[{tool.getTime()}] [ADIDAS] pid: {pid}, status: PREVIEW")
                    continue

                totalStock = 0
                toPrint = ''

                tool.printWarn(f'[{tool.getTime()}] [PID] Product {tool.PURPLE}{res["id"]}{tool.ENDC} link: {tool.PURPLE}{self.getPageOf(pid)}{tool.ENDC}')
                for variation in res['variation_list']:
                    toPrint=f'[{tool.getTime()}] [PID info] Size: {variation["size"]}{" "*4 if len(str(variation["size"])) == 2 else ""} Stock Available: {variation["availability"]} Status: {variation["availability_status"]}\n'

                    if variation['availability'] > 0:
                        toPrint = tool.printOk(toPrint)
                    else:
                        toPrint = tool.printFail(toPrint)
                    totalStock += variation['availability']
                tool.printBlue(f'Total Stock: {totalStock}\n\n')
                print()

            if self.loop == False:
                break
            sleep(self.timeout)

if __name__ == '__main__':
    main = adidasStockScraper('www.adidas.co.uk')
    main.run(['FX5501', 'IG3081'])
