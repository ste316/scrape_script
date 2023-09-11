# Adidas Stock Scraper
## This is a very easy tool to check stock numbers on Adidas sites

## Get Started
* #### To run this script you need a [python interpreter](https://www.python.org/downloads/) and make sure to include pip during installation
* #### After installing the python interpreter run `pip install -r requirements.txt`
* #### To use this tool you need an Adidas Product Id (pid) 
    * e.g. FX5501
* #### You can retrieve a pid by looking at end of Adidas product page links
    * e.g. https://www.adidas.it/scarpe-stan-smith/FX5501.html
* #### You can monitor multiple product at the same time
    * e.g. `main.run(['FX5501', 'IG3081'])`
* #### You also have to provide:
    * ##### Adidas domain 
    * ##### Timeout
        time in seconds between every interaction with adidas site \
        NOTE lower the timeout faster the update time, more chance of ip being banned
    
    * ##### Loop mode 
        loop mode is the option to keep checking(monitoring) stock numbers \
        NOTE that keep monitoring products may end up in your ip being banned

        * ###### To monitor one or more product is highly recommended the use of proxy
            simply put you proxies in proxies.txt file one per line \
            when running for long period of time or with low timeout you might get your local ip or proxies banned from adidas servers
        
        * ###### if loop mode is disabled, snapshot mode is automatically activated and you will see stock numbers only once 

## General info about Adidas
* For Europe the stock numbers SHOULD be shared between them
    * so you can theoretically run this tool on any region and be informed about every other EU regions
    * some EU regions may have different stock numbers. for example [UK](https://www.adidas.co.uk/) usally does
* Some products may be loaded as `Preview Only` 
    * this means stock numbers are not live yet
    * hopefully will be soon, so it might be worth monitor them
* Either running at low timeout or for long period can lead to get your local ip or your proxies banned from adidas