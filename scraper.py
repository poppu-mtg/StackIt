import os, urllib
import requests
import config

from lxml import html
from globals import Card, specmana

def download_scan(name, expansion):
    name2 = ''.join(e for e in name if e.isalnum())
    localname = name2+'_'+expansion+'.jpg'
    lookupScan = os.path.join('.', 'Scans', localname)
    if os.path.exists(lookupScan):
        return lookupScan

    scanweb = 'http://www.magiccards.info/{set}/en.html'.format(set=expansion)
    scanpage = requests.get(scanweb)
    scantree = html.fromstring(scanpage.content)

    scannumber = scantree.xpath('//a[text()="{name}"]/@href'.format(name=name))
    print(scannumber)
    cardloc = None
    for item in scannumber:
        if item.find("/en/"):
#            cardloc = scannumber[0][:-4].split("/")
            cardloc = item[:-4].split("/")
    if cardloc is None:
        print('ERROR - Could not find {0} ({1})'.format(name, expansion))
    else:
        print(cardloc)

    url = 'http://magiccards.info/scans/en/'+cardloc[1]+'/'+cardloc[3]+'jpg'
    #card scans are labeled via set number -> need to rename the file temporarily to avoid potential overwriting until decklist is finalized
    urllib.urlretrieve(url, cardloc[3]+'jpg')
    os.rename(cardloc[3] + 'jpg', lookupScan)

    return lookupScan


def get_card_info(line):
    ncount_card = 0
    isitland = False
    scan_part1 = ' '

    quantity = int(line.split(" ",1)[0])

    if line.find('/') != -1:
        data = line.split(" / ")

        #split the info at the first blank space
        name = data[0].split(" ",1)[1]
        expansion = data[1].split("\n")[0].lower()
    else:

        #split the info at the first blank space
        quantity = int(line.split(" ",1)[0])
        name = line.split(" ",1)[1].strip()
        expansion = config.Get('cards', name.lower())

    print(name, expansion)
    if quantity == 0:
        return None

    if name.lower() in ["plains","island","swamp","mountain","forest"]:
        isitland = True

    if not isitland:

        #update the cardname as the string to be looked at in the html code of mtgvault.com - finds both CMC and set name
        name_sub = name.replace(",","")
        name_sub = name_sub.replace("'"," ")
        print(name_sub)

        cmcsearch = name_sub.replace(" ","+")
        scansearch = name_sub.replace(" s ","s ")
        scansearch = scansearch.replace(" ","-")
        scansearch = scansearch.lower()
        print cmcsearch,scansearch

        if expansion is None:
            cmcweb = 'http://www.mtgvault.com/cards/search/?q={cmcsearch}&searchtype=name'.format(cmcsearch=cmcsearch)
        else:
            cmcweb = 'http://www.mtgvault.com/cards/search/?q={cmcsearch}&searchtype=name&s={set}'.format(cmcsearch=cmcsearch,set=expansion)
        
        cmcpage = requests.get(cmcweb)
        cmctree = html.fromstring(cmcpage.content)

        scankey = "/card/" + scansearch + '/'

        cmcscan = cmctree.xpath('//a[img[@class="card_image"]]/@href')
#            print cmcscan
        for item in cmcscan:
#                print item,ncount_card
            if scan_part1 != " ":
                return None
            if item.find(scankey) == 0:
                print "found it:",item
                scan_part1 = item.split(scankey)[1]
            ncount_card = ncount_card + 1
        altscan = str(scan_part1.split('/"')[0]).lower()

        expansion = altscan[:-1]

        cmctext = cmctree.xpath('//div[@class="view-card-center"]/p/text()')
        print cmctext

        finallist = []
        for item in cmctext:
            if item[-1] == "}":
                finallist.append(item)
        print finallist

        if cmctext[0].find("Land") != -1:
            altcmc = '*'
        elif not '}' in cmctext[0]:
            # Lotus Bloom, Evermind, and other costless cards.
            altcmc = '**'
        else:
#                cmc_part1 = str(cmctext[0].split(" {")[1])[:-1]
            cmc_part1 = str(finallist[ncount_card-1].split(" {")[1])[:-1]
            altcmc = cmc_part1.split("}{")
            altcmc = [specmana[x] for x in altcmc]
            print name,altcmc

        cost = "".join(altcmc)+"\n"
        print name,expansion,cost

    else:

        #all basic lands will be using Unhinged card art
        if expansion is None:
            expansion = "uh"
        cost = "*\n"
    return Card(name,expansion,cost, quantity)
