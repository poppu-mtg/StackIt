# coding=utf-8
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
import os, urllib.request, urllib.parse, urllib.error
import requests
import config

#needed to remove the accent in 'Pokemon'
import unicodedata

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

    if name.find('/') != -1:
        name = name.split('/')[0]+' ('+name+')'

    scannumber = scantree.xpath('//a[text()="{name}"]/@href'.format(name=name))
    # print(scannumber)
    cardloc = None
    for item in scannumber:
        if item.find("/en/"):
#            cardloc = scannumber[0][:-4].split("/")
            cardloc = item[:-4].split("/")
    if cardloc is None:
        print('ERROR - Could not find {0} ({1})'.format(name, expansion))
    else:
        # print(cardloc)
        pass

    url = 'http://magiccards.info/scans/en/'+cardloc[1]+'/'+cardloc[3]+'jpg'
    urllib.request.urlretrieve(url, cardloc[3]+'jpg')
    os.rename(cardloc[3] + 'jpg', lookupScan)

    return lookupScan

def download_scanPKMN(name, expansion, expID):
    name = unaccent(name[:-1].decode('latin-1'))
    displayname = name
    name = name.replace(' ', '-').replace("'", '')

    localname = 'PKMN-{name}-{expansion}-{expID}.jpg'.format(name=name, expansion=expansion, expID=expID)

    lookupScan = os.path.join('.', 'Scans', localname)

    if os.path.exists(lookupScan):
        return lookupScan, displayname

    pokeurl = 'https://s3.amazonaws.com/pokegoldfish/images/gf/{name}-{expansion}-{expID}.jpg'.format(name=name, expansion=expansion, expID=expID)
    print(pokeurl)
    urllib.request.urlretrieve(pokeurl, localname)
    os.rename(localname, lookupScan)

    return lookupScan, displayname

def download_scanHexCM(mainguy, mainguyscan, typeCM):
    mainguy2 = ''.join(e for e in mainguy if e.isalnum())
    localname = 'HexTCG-'+mainguy2+'_'+typeCM+'.jpg'
    lookupScan = os.path.join('.', 'Scans', localname)

    if os.path.exists(lookupScan):
        return lookupScan

    if mainguyscan == 'cardback-big':
        url = 'https://hex.tcgbrowser.com/images/cards/'+mainguyscan+'.jpg'
    else:
        url = 'https://storage.hex.tcgbrowser.com/big/'+mainguyscan+'.jpg'
        #card scans are labeled via set number -> need to rename the file temporarily to avoid potential overwriting until decklist is finalized
    urllib.urlretrieve(url, localname)
    os.rename(localname, lookupScan)

    return lookupScan

def download_scanHex(name, namescan):
    name2 = ''.join(e for e in name if e.isalnum())
    localname = 'HexTCG-'+name2+'.jpg'
    lookupScan = os.path.join('.', 'Scans', localname)

    if os.path.exists(lookupScan):
        return lookupScan

    url = 'https://storage.hex.tcgbrowser.com/big/'+namescan+'.jpg'
    #card scans are labeled via set number -> need to rename the file temporarily to avoid potential overwriting until decklist is finalized
    urllib.urlretrieve(url, localname)
    os.rename(localname, lookupScan)

    return lookupScan

def get_card_info(line, quantity=None):
    # Tappedout puts tabs instead of spaces.
    # Easiest solution is to just sub them for spaces.
    line = line.replace('\t', ' ')

    ncount_card = 0
    isitland = False
    scan_part1 = None
    #flag for split cards
    splitcost = False
    n_cost = 0
    altcmc_list = []

    if quantity is None:
        data = line.split(" ", 1)
        quantity = int(data[0])
        line = data[1]

    if line.find(' / ') != -1:
        data = line.split(" / ")
        #for non-XML files, we need to check if this is a split card
        if len(data) > 2:
            name = data[0] + ' // ' + data[1]
            expansion = data[2].split("\n")[0].lower()
        else:
            #split the info at the first blank space
            name = data[0]
            expansion = data[1].split("\n")[0].lower()
    else:
        #split the info at the first blank space
        name = line.strip()
        expansion = config.Get('cards', name.lower())

    print('Looking up {0} ({1})'.format(name, expansion))
    if quantity == 0:
        return None

    if name.lower() in ["plains", "island", "swamp", "mountain", "forest"]:
        isitland = True

    if not isitland:

        #update the cardname as the string to be looked at in the html code of mtgvault.com - finds both CMC and set name
        name_sub = name.replace(",", "")
        name_sub = name_sub.replace("'", " ")
        # print(name_sub)

        cmcsearch = name_sub.replace(" ", "+")
        scansearch = name_sub.replace(" s ", "s ")
#        scansearch = scansearch.replace(" ","-")
        if name_sub.find(' // ') != -1:
            scansearch = scansearch.replace(" // ", '-')
        else:
            scansearch = scansearch.replace(" ", "-")
        scansearch = scansearch.lower()
        # print(cmcsearch, scansearch)

        if expansion is None:
            cmcweb = 'http://www.mtgvault.com/cards/search/?q={cmcsearch}&searchtype=name'.format(cmcsearch=cmcsearch)
        else:
            cmcweb = 'http://www.mtgvault.com/cards/search/?q={cmcsearch}&searchtype=name&s={set}'.format(cmcsearch=cmcsearch, set=expansion)

        cmcpage = requests.get(cmcweb)
        cmctree = html.fromstring(cmcpage.content)

        scankey = "/card/" + scansearch + '/'

        cmcscan = cmctree.xpath('//a[img[@class="card_image"]]/@href')
        # print cmcscan
        for item in cmcscan:
            # print item,ncount_card
            if scan_part1 != None:
                continue
            if item.find(scankey) == 0:
                print("found it:", item)
                scan_part1 = item.split(scankey)[1]
            ncount_card = ncount_card + 1
        altscan = str(scan_part1.split('/"')[0]).lower()

        expansion = altscan[:-1]

        cmctext = cmctree.xpath('//div[@class="view-card-center"]/p/text()')
        # print(cmctext)

        finallist = []
        for item in cmctext:
            if item[-1] == "}":
                finallist.append(item)
        # print(finallist)

        if cmctext[0].find("Land") != -1:
            altcmc = '*'
        elif not '}' in cmctext[0]:
            # Lotus Bloom, Evermind, and other costless cards.
            altcmc = '**'
        else:
#                cmc_part1 = str(cmctext[0].split(" {")[1])[:-1]
            if finallist[ncount_card-1].find(' // ') != -1:
                splitcost = True
                for item in finallist[0].split(' //'):
                    altcmc_list.append(item.split(" {")[1][:-1].split("}{"))
                    # print(name, altcmc_list[n_cost])
                    n_cost += 1
            else:
                cmc_part1 = str(finallist[ncount_card-1].split(" {")[1])[:-1]
                altcmc = cmc_part1.split("}{")
                altcmc = [specmana[x] for x in altcmc]
                # print(name, altcmc)

        cost = ''
        if splitcost:
            for n in range(n_cost):
                cost += "".join(altcmc_list[n])+'/'
            cost = cost[:-1]+"\n"
        else:
            cost = "".join(altcmc)+"\n"
        print((name, expansion, cost))

    else:

        #all basic lands will be using Unhinged card art
        if expansion is None:
            expansion = "uh"
        cost = "*\n"
    return Card(name, expansion, cost, quantity, collector_num=None)

def unaccent(text):
    text =  ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))
    text = text.encode('ASCII', 'ignore').replace('PokAmon','Pokemon')
    return text
