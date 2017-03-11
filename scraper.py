import os, urllib
import requests

from lxml import html


def download_scan(name, set):
    name2 = ''.join(e for e in name if e.isalnum())
    localname = name2+'_'+set+'.jpg'
    lookupScan = os.path.join('.', 'Scans', localname)
    if os.path.exists(lookupScan):
        return lookupScan

    scanweb = 'http://www.magiccards.info/{set}/en.html'.format(set=set)
    scanpage = requests.get(scanweb)
    scantree = html.fromstring(scanpage.content)

    scannumber = scantree.xpath('//a[text()="{name}"]/@href'.format(name=name))
    print(scannumber)
    for item in scannumber:
        if item.find("/en/"):
#            cardloc = scannumber[0][:-4].split("/")
            cardloc = item[:-4].split("/")
    print(cardloc)

    url = 'http://magiccards.info/scans/en/'+cardloc[1]+'/'+cardloc[3]+'jpg'
    #card scans are labeled via set number -> need to rename the file temporarily to avoid potential overwriting until decklist is finalized
    urllib.urlretrieve(url, cardloc[3]+'jpg')
    os.rename(cardloc[3] + 'jpg', lookupScan)

    return lookupScan

