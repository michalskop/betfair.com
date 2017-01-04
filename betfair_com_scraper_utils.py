import json
from lxml import html, etree
import re
import requests
import time

import settings


def scrape_race(race):
    url = settings.betfair_url3 + race
    r = requests.get(url)
    data = {}
    if r.status_code == 200:
        dataj = r.json()
        for en in dataj['eventTypes'][0]['eventNodes']:
            data['state'] = en['marketNodes'][0]['state']
            data['runners'] = en['marketNodes'][0]['runners']
    return data


def scrape_subraces(href):
    url = settings.betfair_url + href + settings.betfair_url2_end
    r = requests.get(url)
    data = []
    if r.status_code == 200:
        datajson = r.json()
        domtree = html.fromstring(datajson['children'])
        ul = domtree.xpath('//ul[@class="children"]')[0]
        lis = ul.xpath('li')
        for li in lis:
            item = {}
            item['title'] = li.xpath('a/@market-name')[0]
            try:
                item['identifier'] = li.xpath('a/@market-id')[0]
                t = time.localtime(int(li.xpath('a/@market-time')[0]) / 1000)
                item['date'] = time.strftime('%Y-%m-%d %H:%M:%S', t)
                data.append(item)
            except:
                data = data + scrape_subraces(li.xpath('a/@href')[0])
    return(data)


def scrape_races(fdir):
    url = settings.betfair_url + fdir
    r = requests.get(url)
    data = []
    if r.status_code == 200:
        domtree = html.fromstring(r.text)
        ul = domtree.xpath('//ul[@class="children"]')[0]
        lis = ul.xpath('li')
        for li in lis:
            item = {}
            item['title'] = li.xpath('a/@market-name')[0]
            item['href'] = li.xpath('a/@href')[0]
            item['identifier'] = re.search('[0-9]{1,}', item['href']).group(0)
            data.append(item)
    return data


if __name__ == "__main__":
    # test:
    da = scrape_races('politics')
    print(da)
    dat = []
    for row in da:
        dat = dat + scrape_subraces(row['href'])
    print(dat)
    for row in dat:
        data = scrape_race(row['identifier'])
        print(data)
