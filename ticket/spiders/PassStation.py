__author__ = 'zhouguobing'
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request
from scrapy import log
from os import path
import os
import requests
import cPickle as cp
import json

class TicketSpider(CrawlSpider):
    name = 'pass'
    allowed_domains = ['kyfw.12306.cn']
    start_urls = []

    rules = (
        #Rule(SgmlLinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def __init__(self):
        print __file__
        #requests.packages.urllib3.disable_warnings()
        self.format = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=%s&from_station_telecode=%s&to_station_telecode=%s&depart_date=2015-06-20"
        path = os.path.abspath('./ticket/data/trains-20150615.csv')
        ftrain_list =  open(path,"r")
        self.start_urls = []
        for line in ftrain_list:
            items = line.strip().split(",")
            self.start_urls.append(self.format%(items[0],items[2],items[3]))

        path = os.path.abspath('./ticket/data/PassStation-20150615.csv')
        self.ftrains = open(path,"w")
        pass

    def parse(self, response):
        """
        default parse method, rule is not useful now
        """
        #print response.body
        #url = ""
        #yield Request(url, callback=self.parse)
        traindict = json.loads(response.body)
        # print traindict
        if traindict == -1:
            return self.nextreq(-1)

        status = traindict["status"]
        httpstatus = traindict["httpstatus"]
        # print status,httpstatus
        if status == True and httpstatus == 200:
            if not "data" in traindict["data"]:
                pass

            self.ftrains.write(json.dumps(traindict["data"]["data"]))
            self.ftrains.write("\n")
        
    def nextreq(self, type):
        if type == -1:
            self.black_list[self.to_index][self.from_index] = 1
        
        while True:
            self.to_index += 1
            if self.to_index >= self.slen:
                self.from_index += 1
                self.to_index = self.to_index % self.slen
            if self.from_index >= self.slen:
                return None
            if  self.black_list[self.from_index][self.to_index] == 0:
                break


        url = "https://kyfw.12306.cn/otn/lcxxcx/query?"\
                           "purpose_codes=ADULT&queryDate=2015-06-26&"\
                           "from_station=%s&to_station=%s"%(self.slist[self.from_index],self.slist[self.to_index])
        request = Request(url, callback= self.parse, errback=self.pro_error)
        return request

    def pro_error(self, failure):
        print "%s to %s error"%(self.slist[self.from_index],self.slist[self.to_index])
        self.nextreq(0)
        pass

    def determine_level(self, response):
        """
        determine the index level of current response, so we can decide wether to continue crawl or not.
        level 1: people/[a-z].html
        level 2: people/[A-Z][\d+].html
        level 3: people/[a-zA-Z0-9-]+.html
        level 4: search page, pub/dir/.+
        level 5: profile page
        """
        import re
        url = response.url
        if re.match(".+/[a-z]\.html", url):
            return 1
        elif re.match(".+/[A-Z]\d+.html", url):
            return 2
        elif re.match(".+/people-[a-zA-Z0-9-]+", url):
            return 3
        elif re.match(".+/pub/dir/.+", url):
            return 4
        elif re.match(".+/search/._", url):
            return 4
        elif re.match(".+/pub/.+", url):
            return 5
        log.msg("Crawl cannot determine the url's level: " + url)
        return None

    def save_to_file_system(self, level, response):
        """
        save the response to related folder
        """
        if level in [1, 2, 3, 4, 5]:
            fileName = self.get_clean_file_name(level, response)
            if fileName is None:
                return

            fn = path.join(self.settings["DOWNLOAD_FILE_FOLDER"], str(level), fileName)
            self.create_path_if_not_exist(fn)
            if not path.exists(fn):
                with open(fn, "w") as f:
                    f.write(response.body)

    def get_clean_file_name(self, level, response):
        """
        generate unique linkedin id, now use the url
        """
        url = response.url
        if level in [1, 2, 3]:
            return url.split("/")[-1]

        linkedin_id = self.get_linkedin_id(url)
        if linkedin_id:
            return linkedin_id
        return None

    def get_linkedin_id(self, url):
        find_index = url.find("www.linkedin.com/")
        if find_index >= 0:
            log.msg(url, url[find_index + 13:].replace('/', '-'))
            return url[find_index + 13:].replace('/', '-')
        return None

    def get_follow_links(self, level, hxs):
        if level in [1, 2, 3]:
            relative_urls = hxs.select("//ul[@class='directory']/li/a/@href").extract()
            relative_urls = ["http://www.linkedin.com" + x for x in relative_urls]
            return relative_urls
        elif level == 4:
            relative_urls = relative_urls = hxs.select("//ol[@id='result-set']/li/h2/strong/a/@href").extract()
            relative_urls = ["http://www.linkedin.com" + x for x in relative_urls]
            return relative_urls

    def create_path_if_not_exist(self, filePath):
        if not path.exists(path.dirname(filePath)):
            os.makedirs(path.dirname(filePath))

