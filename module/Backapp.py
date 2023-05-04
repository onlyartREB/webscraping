import os
import django

import cfscrape
import pandas as pd
from bs4 import BeautifulSoup as soup, BeautifulSoup ,_s
import requests
from threading import Timer
import sqlite3
import models
from ML import classifer, vectorizer
from my_app.presse.models import Article, Health, Science, Sport

try:
    sqlite3.connect("db")
    print("connected to db")
except:
    print("connection error")

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
def get_proxies():
    # Find a free proxy provider website
    # Scrape the proxies
    proxy_web_site = 'https://free-proxy-list.net/'
    response = requests.get(proxy_web_site)
    page_html = response.text
    page_soup = _s(page_html, "html.parser")
    containers = page_soup.find_all("div", {"class": "table-responsive"})[0]
    ip_index = [8 * k for k in range(80)]
    proxies = set()

    for i in ip_index:
        ip = containers.find_all("td")[i].text
        port = containers.find_all("td")[i + 1].text
        https = containers.find_all("td")[i + 6].text
        print("\nip address : {}".format(ip))
        print("port : {}".format(port))
        print("https : {}".format(https))

        if https == 'yes':
            proxy = ip + ':' + port
            proxies.add(proxy)
    return proxies


def check_proxies():
    # check the proxies and save the working ones
    proxies = get_proxies()
    test_url = 'https://httpbin.org/ip'
    for i in proxies:
        print("\nTrying to connect with proxy: {}".format(i))
        try:
            response = requests.get(test_url, proxies={"http": i, "https": i}, timeout=5)
            print("working proxy found")
            return i
            break
        except:
            print("Connnection error")
    return 0
#getting the content of not protected sites
def connectSimple(url):
    r = requests.get(url)
    if r.status_code == 200:
        print("connected")
        soup = BeautifulSoup(r.text, "html.parser")
    return soup
#getting the content from protected sites
def connectProxy(url) :
    working_proxy = check_proxies()
    if working_proxy != 0:
        scraper = cfscrape.create_scraper()
        proxies = {"http": working_proxy, "https": working_proxy}
        resp = scraper.get(url, proxies=proxies, allow_redirects=True, timeout=(10, 20))
        soup= BeautifulSoup(resp.text, "html.parser")
        return soup
    else:
        print ("no working proxy found")



def getinfo(soup,x, y, z):

    for title in (soup.findAll(x, {"class": y})[0:10]):
        c=0
        for article in (Article.objects.filter(titre=title.get_text().encode("utf-8"),source=z)):
            c=c+1
        if c==0 :
            print("updating")
            t=(title.get_text().encode("utf-8"))


            if title.get('href')==None  :
                u=(title.a.get('href'))


            else :
                u=(title.get('href'))
            if (y=="aps"):
                u=("http://www.aps.dz"+(title.get('href')))

            article = Article(titre=t, url=u , source=z)
            article.save()
            classify(article)
        else : print("not updating")

df=[]
site=[]

# the list of sites we want to work with them with the parameters we need to work with
# later if we want to add other sites we only add them in this list without any changes in code
#we can also make these sites as csv file to optimise our work
site.append(("http://www.aps.dz/","h4", "allmode-title-list", "Title","aps",57600))
site.append(("https://www.elwatan.com/category/a-la-une/actualite/","h3", "title-14","Title","elwatan",86400))
site.append(("https://www.liberte-algerie.com/a-la-une/","a", "title", "Title","liberte",14400))
site.append(("https://www.tsa-algerie.com/","article", "ntdga", "Title","TSA",3600))
def work(i):
    print("working on :" + site[i][4])
    url = site[i][0]
    try:  # for checking if the site is secured or we need to connect with proxy
        #r = requests.get(url)
        soup =connectSimple(url)
    except:
        soup =connectProxy(url)
    getinfo(soup, site[i][1], site[i][2], site[i][4])
def classify(article):


    news=article
    title = news.titre
    doc_term_matrix = vectorizer.transform(title)
    classifer.predict(doc_term_matrix)
    if classifer.predict(doc_term_matrix)=="sante":
        health=Health(Article=article)
        health.save()
    if classifer.predict(doc_term_matrix)=="science":
        science=Science(Article=article)
        science.save()
    if classifer.predict(doc_term_matrix)=="sport":
        sport=Sport(Article=article)
        sport.save()
#usage
print("starting...")
dictionary1 = pd.read_csv("Health.csv",encoding='utf-8-sig')
pattern1 ='|'.join(dictionary1["maladie"])
dictionary2 = pd.read_csv("science.csv",header=1)
pattern2 = '|'.join(dictionary2["la biologie"])
dictionary3 = pd.read_csv("sport.csv",header=1)
pattern3 = '|'.join(dictionary3['spectateur de sport'])

rt1= RepeatedTimer(site[0][5],work,0)
rt1._run()
rt2= RepeatedTimer(site[1][5],work,1)
rt2._run()
rt3= RepeatedTimer(site[2][5],work,2)
rt3._run()
rt4= RepeatedTimer(site[3][5],work,3)
rt4._run()