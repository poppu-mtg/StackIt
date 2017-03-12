import os, sys, glob
import re

#Image manipulation
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

#Check input format
import mmap

#XML parsing
import xml.etree.ElementTree

#HTML parsing
from lxml import html
import requests

import scraper

#ensure that mana costs greater than 9 (Kozilek, Emrakul...) aren't misaligned
adjustcmc = False
check9 = '0123456'

def GenerateCMC(name, set):
    global adjustcmc
    name2 = ''.join(e for e in name if e.isalnum())
    diskcost = cost.strip().replace('*', '_')
    lookupCMC = os.path.join('CmcCache', '{cost}.png'.format(cost=diskcost))
    if os.path.exists(lookupCMC):
        print("Card CMC' already been used, loading...")
        tap0 = Image.open(lookupCMC)
        if tap0.mode != 'RGBA':
            tap0 = tap0.convert('RGBA')
        cmc.paste(tap0, (0,0), mask=tap0)
        #still need to check cost adjustment...
        for n in range(len(cost)-1):
            if (cost[n] == '1') and (check9.find(cost[n+1]) != -1):
                adjustcmc = True
    else:
        greaterthan9 = False
        for n in range(len(cost)-1):
            #reset the large mana cost markers
            if greaterthan9:
                greaterthan9 = False
                adjustcmc = True
                continue
            #lands have no mana cost and are tagged with '*'
            if cost[n] == "*":
                continue
            else:
                if (cost[n] == '1') and (check9.find(cost[n+1]) != -1):
                    finalcost = cost[n]+cost[n+1]
                    greaterthan9 = True
                else:
                    finalcost = cost[n]
                symbol = 'Mana/Mana_'+finalcost+'.png'

                tap0 = Image.open(symbol)
                if tap0.mode != 'RGBA':
                    tap0 = tap0.convert('RGBA')

                tap = tap0.resize((16,16))
                cmc.paste(tap, (15*n,0), mask=tap)
        cmc.save(lookupCMC)

ncount = 0
nstep = 1

if not os.path.exists('./Scans'):
    os.mkdir('./Scans')
if not os.path.exists('./CmcCache'):
    os.mkdir('./CmcCache')

#some position initialization
xtop = 8
xbot = 304

ytop = 11.5
ybot = 45.25

#load the MTG text fonts
fnt = ImageFont.truetype("beleren-webfonts/belerensmallcaps-bold-webfont.ttf", 14)
fnt_title = ImageFont.truetype("beleren-webfonts/belerensmallcaps-bold-webfont.ttf", 18)

#create basic landtypes database:
basics = ["plains","island","swamp","mountain","forest"]

#create a dictionary for non-basic mana:
specmana = {'0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '10': '10', '11': '11', '12': '12', '13': '13', '14': '14', '15': '15', '16': '16', 'X': 'X', 'C': 'C', 'W': 'W', 'U': 'U', 'B': 'B', 'R': 'R', 'G': 'G', 'PW': 'P', 'PU': 'Q', 'PB': 'S', 'PR': 'T', 'PG': 'V', '2W': 'Y', '2U': 'Z', '2B': '@', '2R': 'A', '2G': 'D', 'WU': 'E', 'UB': 'F', 'BR': 'H', 'RG': 'I', 'GW': 'J', 'WB': 'K', 'UR': 'L', 'BG': 'M', 'RW': 'N', 'GU': 'O'}

#check the input format
isXML = False

# create a horizontal gradient...
gradient = Image.new('L', (255,1))

#map the gradient
#for x in range(64):
#    gradient.putpixel((x,0),254)
#for x in range(64):
#    gradient.putpixel((63+x,0),max(254-x,0))
#for x in range(128):
#    gradient.putpixel((127+x,0),max(int(190-1.5*x),0))
for x in range(128):
    gradient.putpixel((x,0),int(1.5*x))
for x in range(64):
    gradient.putpixel((127+x,0),190+x)
for x in range(64):
    gradient.putpixel((190+x,0),254)

#create a header with the deck's name
title = Image.new("RGB", (280,34), "black")
drawtitle = ImageDraw.Draw(title)
drawtitle.text((10, 7),os.path.basename(str(sys.argv[1]))[0:-4],(250,250,250), font=fnt_title)

#create a Sideboard partition
sideboard = Image.new("RGB", (280,34), "black")
drawtitle = ImageDraw.Draw(sideboard)
drawtitle.text((10, 7),"Sideboard",(250,250,250), font=fnt_title)


#open user input decklist
decklist1 = open(str(sys.argv[1]), 'r')

#determine if input decklist is in XML format
isDeckXML = mmap.mmap(decklist1.fileno(), 0, access=mmap.ACCESS_READ)
if isDeckXML.find('xml') != -1:
    print 'Warning - input decklist is in XML format'
    isXML = True
    
#check for readable content
if isXML:

    info = xml.etree.ElementTree.parse(str(sys.argv[1])).getroot()

    modoformat = {}

    for atype in info.findall('Cards'):
        if atype.get('Sideboard') == "true":
            continue
        else:
            if atype.get('Name') in modoformat:
                modoformat[atype.get('Name')] += int(atype.get('Quantity'))
            else:
                modoformat[atype.get('Name')] = int(atype.get('Quantity'))

    modonames = list(modoformat.keys())
    modoquant = [modoformat[x] for x in modonames]
    ncount = len(modonames)
    print ncount, modonames, modoquant
    
else:

    for lines1 in decklist1:
    
        if lines1[0] == '#':
            continue

        ncount = ncount +1

decklist1.close()

#define the size of the canvas, incl. space for the title header
deckheight = 34*(ncount+1)
deckwidth = 280

deck = Image.new("RGB", (deckwidth, deckheight), "white")

deck.paste(title, (0,0))

#now read the decklist
if not isXML:

    #parse an ASCII decklist
    decklist = open(str(sys.argv[1]), 'r')

    for lines in decklist:

        ncount_card = 0

        #necessary for appropriate treatment of the missing mana cost of lands
        isitland = 0
        isitspecland = 0

        #reset the new parser
        set = ' '
        scan_part1 = ' '

        if lines[0] == '#':
            continue
        
        if lines[0] == '\n':
            # We're at the Sideboard now.
            deck.paste(sideboard, (0,34*nstep))
            nstep = nstep + 1
            continue

        #this step checks whether a specific art is requested by the user - provided via the set name

        if lines.find('/') != -1:

            data = lines.split(" / ")

            #split the info at the first blank space
            quantity = int(data[0].split(" ",1)[0])
            name = data[0].split(" ",1)[1]

            if quantity == 0:
                continue

            set = data[1].split("\n")[0].lower()

            for landtype in basics:

                if name.lower() == landtype:

                    isitland = 1

            if isitland != 1:

                #update the cardname as the string to be looked at in the html code of mtgvault.com - finds both CMC and set name
                name_sub = name.replace(",","")
                name_sub = name_sub.replace("'"," ")
                print name_sub

                cmcsearch = name_sub.replace(" ","+")
                scansearch = name_sub.replace(" s ","s ")
                scansearch = scansearch.replace(" ","-")
                scansearch = scansearch.lower()
                print cmcsearch,scansearch

                cmcweb = 'http://www.mtgvault.com/cards/search/?q={cmcsearch}&searchtype=name&s={set}'.format(cmcsearch=cmcsearch,set=set)

                cmcpage = requests.get(cmcweb)
                cmctree = html.fromstring(cmcpage.content)

                scankey = "/card/" + scansearch + '/'

                cmcscan = cmctree.xpath('//a[img[@class="card_image"]]/@href')
    #            print cmcscan
                for item in cmcscan:
    #                print item,ncount_card
                    if scan_part1 != " ":
                        continue
                    if item.find(scankey) == 0:
                        print "found it:",item
                        scan_part1 = item.split(scankey)[1]
                    ncount_card = ncount_card + 1

                cmctext = cmctree.xpath('//div[@class="view-card-center"]/p/text()')
                print cmctext

                finallist = []
                for item in cmctext:
                    if item[-1] == "}":
                        finallist.append(item)
                print finallist

                if cmctext[0].find("Land") != -1:
                    isitspecland = 1
                else:
    #                cmc_part1 = str(cmctext[0].split(" {")[1])[:-1]
                    cmc_part1 = str(finallist[ncount_card-1].split(" {")[1])[:-1]
                    altcmc = cmc_part1.split("}{")
                    altcmc = [specmana[x] for x in altcmc]
                    print name,altcmc

                if isitspecland == 1:
                    cost = "*\n"
                else:
                    cost = "".join(altcmc)+"\n"

            else:

                cost = "*\n"

            print name,set,cost

        else:

            #split the info at the first blank space
            quantity = int(lines.split(" ",1)[0])
            name = lines.split(" ",1)[1].strip()

            if quantity == 0:
                continue

            for landtype in basics:

                if name.lower() == landtype:

                    isitland = 1

            if isitland != 1:

                #update the cardname as the string to be looked at in the html code of mtgvault.com - finds both CMC and set name
                name_sub = name.replace(",","")
                name_sub = name_sub.replace("'"," ")
                print name_sub

                cmcsearch = name_sub.replace(" ","+")
                scansearch = name_sub.replace(" s ","s ")
                scansearch = scansearch.replace(" ","-")
                scansearch = scansearch.lower()
                print cmcsearch,scansearch

                cmcweb = 'http://www.mtgvault.com/cards/search/?q={cmcsearch}&searchtype=name'.format(cmcsearch=cmcsearch)

                cmcpage = requests.get(cmcweb)
                cmctree = html.fromstring(cmcpage.content)

                scankey = "/card/" + scansearch + '/'

                cmcscan = cmctree.xpath('//a[img[@class="card_image"]]/@href')
    #            print cmcscan
                for item in cmcscan:
    #                print item,ncount_card
                    if scan_part1 != " ":
                        continue
                    if item.find(scankey) == 0:
                        print "found it:",item
                        scan_part1 = item.split(scankey)[1]
                    ncount_card = ncount_card + 1
                altscan = str(scan_part1.split('/"')[0]).lower()

                set = altscan[:-1]

                cmctext = cmctree.xpath('//div[@class="view-card-center"]/p/text()')
                print cmctext

                finallist = []
                for item in cmctext:
                    if item[-1] == "}":
                        finallist.append(item)
                print finallist

                if cmctext[0].find("Land") != -1:
                    isitspecland = 1
                else:
    #                cmc_part1 = str(cmctext[0].split(" {")[1])[:-1]
                    cmc_part1 = str(finallist[ncount_card-1].split(" {")[1])[:-1]
                    altcmc = cmc_part1.split("}{")
                    altcmc = [specmana[x] for x in altcmc]
                    print name,altcmc

                if isitspecland == 1:
                    cost = "*\n"
                else:
                    cost = "".join(altcmc)+"\n"
                print name,set,cost

            else:

                #all basic lands will be using Unhinged card art
                set = "uh"
                cost = "*\n"

        #all card arts are found on magiccards.info
    #    cmcscan = cmctree.xpath('//a[img]/@href')

        lookupScan = scraper.download_scan(name,set)

        img = Image.open(lookupScan)

        #check if im has Alpha band...
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        #resize the gradient to the size of im...
        alpha = gradient.resize(img.size)

        #put alpha in the alpha band of im...
        img.putalpha(alpha)

        bkgd = Image.new("RGB", img.size, "black")
        bkgd.paste(img, (0,0), mask=img)

        cut = bkgd.crop((xtop+12, ytop+125, xbot, ybot+125))

        draw = ImageDraw.Draw(cut)
        #create text outline
        draw.text((6, 6),str(quantity)+'  '+name,(0,0,0), font=fnt)
        draw.text((8, 6),str(quantity)+'  '+name,(0,0,0), font=fnt)
        draw.text((6, 8),str(quantity)+'  '+name,(0,0,0), font=fnt)
        draw.text((8, 8),str(quantity)+'  '+name,(0,0,0), font=fnt)
        #enter text
        draw.text((7, 7),str(quantity)+'  '+name,(250,250,250), font=fnt)

        cmc = Image.new('RGBA',(16*len(cost), 16))

        GenerateCMC(name, set)

        #place the cropped picture of the current card
        deck.paste(cut, (0,34*nstep))

        #adjust cmc size to reflex manacost greater than 9
        if adjustcmc:
            deck.paste(cmc, (280-15*(len(cost)-1),8+34*nstep), mask=cmc)
            adjustcmc = False
        else:
            deck.paste(cmc, (280-15*len(cost),8+34*nstep), mask=cmc)

        nstep = nstep+1

    decklist.close()

else:

    #parse the XML decklist
    doitFirst = []
    doitLast = []
    sizeFirst = 0
    sizeLast = 0
    
    for n in range(ncount):
    
        ncount_card = 0

        #necessary for appropriate treatment of the missing mana cost of lands
        isitland = 0
        isitspecland = 0

        #reset the new parser
        set = ' '
        scan_part1 = ' '
        
        name = modonames[n]
        quantity = modoquant[n]

        for landtype in basics:
            if name.lower() == landtype:
                isitland = 1

#        print quantity,name,isitland
    
        if isitland != 1:

            #update the cardname as the string to be looked at in the html code of mtgvault.com - finds both CMC and set name
            name_sub = name.replace(",","")
            name_sub = name_sub.replace("'"," ")
            print name_sub

            cmcsearch = name_sub.replace(" ","+")
            scansearch = name_sub.replace(" s ","s ")
            scansearch = scansearch.replace(" ","-")
            scansearch = scansearch.lower()
            print cmcsearch,scansearch

            cmcweb = 'http://www.mtgvault.com/cards/search/?q={cmcsearch}&searchtype=name'.format(cmcsearch=cmcsearch)

            cmcpage = requests.get(cmcweb)
            cmctree = html.fromstring(cmcpage.content)

            scankey = "/card/" + scansearch + '/'

            cmcscan = cmctree.xpath('//a[img[@class="card_image"]]/@href')
            for item in cmcscan:
                if scan_part1 != " ":
                    continue
                if item.find(scankey) == 0:
                    print "found it:",item
                    scan_part1 = item.split(scankey)[1]
                ncount_card = ncount_card + 1
            altscan = str(scan_part1.split('/"')[0]).lower()

            set = altscan[:-1]

            cmctext = cmctree.xpath('//div[@class="view-card-center"]/p/text()')
            print cmctext

            finallist = []
            for item in cmctext:
                if item[-1] == "}":
                    finallist.append(item)
            print finallist

            if cmctext[0].find("Land") != -1:
                isitspecland = 1
            else:
                cmc_part1 = str(finallist[ncount_card-1].split(" {")[1])[:-1]
                altcmc = cmc_part1.split("}{")
                altcmc = [specmana[x] for x in altcmc]
                print name,altcmc

            if isitspecland == 1:
                cost = "*\n"
            else:
                cost = "".join(altcmc)+"\n"
            print name,set,cost

        else:

            #all basic lands will be using Unhinged card art
            set = "uh"
            cost = "*\n"

        print quantity,name,set,cost
        
        if cost == "*\n":
            doitLast.append(quantity)
            doitLast.append(name)
            doitLast.append(set)
            doitLast.append(cost)
            sizeLast = sizeLast + 1
        else:
            doitFirst.append(quantity)
            doitFirst.append(name)
            doitFirst.append(set)
            doitFirst.append(cost)
            sizeFirst = sizeFirst + 1

    doitAll = doitFirst+doitLast
    sizeAll = sizeFirst+sizeLast
    print doitAll,sizeAll
            
    for nAll in range(sizeAll):
        quantity = doitAll[0+4*nAll]
        name = doitAll[1+4*nAll]
        set = doitAll[2+4*nAll]
        cost = doitAll[3+4*nAll]

        lookupScan = scraper.download_scan(name, set)

        img = Image.open(lookupScan)

        #check if im has Alpha band...
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        #resize the gradient to the size of im...
        alpha = gradient.resize(img.size)

        #put alpha in the alpha band of im...
        img.putalpha(alpha)

        bkgd = Image.new("RGB", img.size, "black")
        bkgd.paste(img, (0,0), mask=img)

        cut = bkgd.crop((xtop+12, ytop+125, xbot, ybot+125))

        draw = ImageDraw.Draw(cut)
        #create text outline
        draw.text((6, 6),str(quantity)+'  '+name,(0,0,0), font=fnt)
        draw.text((8, 6),str(quantity)+'  '+name,(0,0,0), font=fnt)
        draw.text((6, 8),str(quantity)+'  '+name,(0,0,0), font=fnt)
        draw.text((8, 8),str(quantity)+'  '+name,(0,0,0), font=fnt)
        #enter text
        draw.text((7, 7),str(quantity)+'  '+name,(250,250,250), font=fnt)

        cmc = Image.new('RGBA',(16*len(cost), 16))

        lookupCMC = GenerateCMC(name, set)

        #place the cropped picture of the current card
        deck.paste(cut, (0,34*nstep))

        #adjust cmc size to reflex manacost greater than 9
        if adjustcmc:
            deck.paste(cmc, (280-15*(len(cost)-1),8+34*nstep), mask=cmc)
            adjustcmc = False
        else:
            deck.paste(cmc, (280-15*len(cost),8+34*nstep), mask=cmc)

        nstep = nstep+1
        
            
deck = deck.crop((0, 0, deckwidth-10, deckheight))

#deck.save("deck.png")
deck.save(str(sys.argv[1])[0:-4]+".png")
