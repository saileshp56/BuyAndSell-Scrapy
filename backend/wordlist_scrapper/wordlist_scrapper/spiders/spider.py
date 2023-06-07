from io import StringIO
from functools import partial
from scrapy.http import Request
from scrapy.spiders import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.item import Item
import sys

def find_all_substrings(string, sub):

    import re
    starts = [match.start() for match in re.finditer(re.escape(sub), string)]
    return starts

class WebsiteSpider(CrawlSpider):

    name = "keybas"

    #French
    #allowed_domains = ["achatsetventes.gc.ca"]
    #start_urls = ["https://achatsetventes.gc.ca"]
    #rules = [Rule(LinkExtractor(deny=('search/', 'appels-d-offres/', 'avis-d-attribution/', 'contrats-octroyes/', 'numero-d-identification-des-biens-et-services/', 'offres-a-commandes-et-d-arrangements-en-matiere-d-approvisionnement/', 'demandez-votre-propre-lettre-des-contrats-octroyes-au-fournisseur')), follow=True, callback="check_buzzwords")]
    # print('First param:'+sys.argv[1]+'#')

    #English
    
    allowed_domains = [""] #what domains the spider is allowed to crawl
    
    start_urls = [""] #where the branching starts
    # rules = [Rule(LinkExtractor(deny=('search/', 'tender-notice/', 'award-notice/', 'contract-history/', 'goods-and-services-identification-number/', 'standing-offers-and-supply-arrangements/', 'request-your-own-supplier-contract-history-letter', 'feed?')), follow=True, callback="check_buzzwords")]
    #exempts the deny terms from crawl (when in url)
    rules = ''

    def __init__(self, domains='', start='', *args, **kwargs):
        # raise Exception("Exception for error handling testing - Sailesh (dev)")
        self.allowed_domains = [f'{domains}']  # py3
        self.start_urls = [f'{start}']  # py3

        deny_args = sys.argv[5:]
        deny_set = set()
        for x in deny_args[2::2]:
              deny_set.add(x[x.find('=')+1:])
        print("Denying the following urls: ", deny_set)


        self.rules = [Rule(LinkExtractor(deny=deny_set), follow=True, callback="check_buzzwords")]
        
        super().__init__(**kwargs)  # python3
        
          



    #took out deny rule for to 'policy-and-guidelines'
    crawl_count = 0
    words_found = 0
    


    def check_buzzwords(self, response):

        self.__class__.crawl_count += 1

        crawl_count = self.__class__.crawl_count

        wordlist = [
            "buy",
            #"Office of Small",
            #"Medium Enterprises",
            #"Office of Small and Medium Enterprises",
            #"BPME",
            #"Bureau des petites",
            #"moyennes entreprises",
            #"Bureau des petites et moyennes entreprises",
            ]
        
        #put in keyword you're looking for (in code of pages)

        url = response.url
        pagetitle = response.xpath("//meta[@name='dcterms.title']/@content").get()
        #error = response.errback
        contenttype = response.headers.get("content-type", "").decode('utf-8').lower()
        data = response.body.decode('utf-8')

        for word in wordlist:
                substrings = find_all_substrings(data, word)
                for pos in substrings:
                        ok = False
                        if not ok:
                                self.__class__.words_found += 1
                                print('"' + pagetitle + '",' + url) #prints to test.csv
        return Item()

    def _requests_to_follow(self, response):
        if getattr(response, "encoding", None) != None:
                return CrawlSpider._requests_to_follow(self, response)
        else:
                return []

        #This is how you run the spider $ scrapy crawl keybas > output/.csv
        #fetwi^^^
        #scrapy crawl keybas > test.csv
        #sailesh^^^
# print('#Hello from python#', sys.argv[1])
