import os
import requests

from lxml import html


def DownloadScan(name, set):
    scanweb = 'http://www.magiccards.info/{set}/en.html'.format(set=set)
    scanpage = requests.get(scanweb)
    scantree = html.fromstring(scanpage.content)

    scannumber = scantree.xpath('//a[text()="{name}"]/@href'.format(name=name))
    print scannumber
    for item in scannumber:
        if item.find("/en/"):
#            cardloc = scannumber[0][:-4].split("/")
            cardloc = item[:-4].split("/")
    print cardloc

    name2 = ''.join(e for e in name if e.isalnum())
    localname = name2+'_'+set+'.jpg'

    #get the jpg file of the card scan -- ONLY if not already in Scans/
    lookupScan = os.path.join('.', 'Scans', localname)
#    print "lookupScan = ",lookupScan

    if os.path.exists(lookupScan):
        print "Card art already been used, loading..."
    else:
        cardpic = 'curl -O http://magiccards.info/scans/en/'+cardloc[1]+'/'+cardloc[3]+'jpg'
        os.system(cardpic)
        #card scans are labeled via set number -> need to rename the file temporarily to avoid potential overwriting until decklist is finalized
        os.rename(cardloc[3] + 'jpg', lookupScan)

    return lookupScan

