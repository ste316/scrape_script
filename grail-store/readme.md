# Grail Store Scraper and Monitor
## This tool is able to Scrape [Grail Store](https://www.grail-store.com) pages and Monitor specific product page
### is also able to send discord webhook notification with product infos

![demo1](https://github.com/ste316/scrape_script/blob/main/grail-store/demo/scraper_demo1.png)
![demo2](https://github.com/ste316/scrape_script/blob/main/grail-store/demo/scraper_demo2.png)

## Get Started
* #### To run this script you need a [python interpreter](https://www.python.org/downloads/) and make sure to include pip during installation
* #### After installing the python interpreter run `pip install -r requirements.txt`
* #### Create a file called proxy.txt and copy your proxies, if any
* #### Create a file called settings.json and copy this
```
{
    "discord_multiple_webhook": false,
    "discord_webhook_links": [],
    "discord_icon_url": ""
}
```
* `discord_multiple_webhook` can be true or false, is usefull when you scrape a lot of product and a lot of webhook must be sent, this can lead to a rate limit to discord webhook
* `discord_webhook_links` is a list of discord webhook links as you could understand from its name, [here](https://docs.gitlab.com/ee/user/project/integrations/discord_notifications.html#create-webhook) is a guide to create one 
* `discord_icon_url` must be a link to an image, that will show in webhook notifications

## Scraper
* #### Product List page
    For example you can scrape this [page](https://www.grail-store.com/en/new/) and get all product links in it \
    Now you got a list filled by a lot of product links to scrape and get their infos

* #### Product page
    After you got a list of product links you can easily scrape each of them\
    You will get a lot of info about the product:
    * title
    * sku (the manufacturer id) 
    * sizes available
        * load link for each size
        * add to cart link for each size

* ## Example
Here is an example of a main function to run it both
```
m = mainPageScraper('https://www.grail-store.com/en/new/', {})
all = m.getAllProductsLinks()

s = productScraper({})
s.bulkScraping(all, dump_json=True)
```
You can see that i passed dump_json as True\
In this case you will get saved all product info 
into data.json file, indexed by the SKU of each products

## Monitor
Monitor is usefull when a product is sold out and you want to buy it as soon as it gets stocks\
By running this script you will be notified via discord webhooks with the product info constantly updated\
An updated state is always shown in the running console\
![demo1](https://github.com/ste316/scrape_script/blob/main/grail-store/demo/monitor_demo1.png)