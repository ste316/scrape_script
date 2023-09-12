# Gen Ebay Activity
## this tool is used to promote a product for sale on Ebay creating views to make it appear more wanted

### Get Started
* #### To run this script you need a [python interpreter](https://www.python.org/downloads/) and make sure to include pip during installation
* #### After installing the python interpreter run `pip install -r requirements.txt`
* #### To use this tool you need to enter:
    * ##### ebay product link
        can be any product, also auction, and can be any ebay domains
    * ##### timeout
        time in seconds between every start of an interaction with ebay site \
        NOTE lower the timeout faster the total visit will be executed, more chance of IPs being banned
    * ##### visit number
        number of visit you want for the specified product\
        NOTE if visit number is a huge number is very highly reccomended the use of proxies \
        to make interactions effective use an high timeout with a lot of proxies

    Insert your preference in the bottom of main.py file
    after the if statement `if __name__ == '__main__': `