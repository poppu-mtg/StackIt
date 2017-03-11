import os, sys, glob
import re

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import xml.etree.ElementTree
from lxml import html
import requests

ncount = 0
nstep = 1

storedScans = glob.glob('./Scans/*.jpg')
storedCMCs = glob.glob('./Scans/*.png')

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

#ensure that mana costs greater than 9 (Kozilek, Emrakul...) are taken care of appropriately
greaterthan9 = 0
adjustcmc = 0
check9 = '0123456'

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
drawtitle.text((10, 7),str(sys.argv[1])[0:-4],(250,250,250), font=fnt_title)

#user input as decklist
decklist1 = open(str(sys.argv[1]), 'r')

#check for readable content
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
decklist = open(str(sys.argv[1]), 'r')

for lines in decklist:
    
    ncount_card = 0

    #necessary for appropriate treatment of the missing mana cost of lands
    isitland = 0
    isitspecland = 0

    #reset the new parser
    set = ' '
    scan_part1 = " "

    if lines[0] == '#':
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
        name = lines.split(" ",1)[1][:-1]

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
    lookupScan = './Scans/'+localname
#    print "lookupScan = ",lookupScan
    
    if lookupScan in storedScans:
        print "Card art already been used, loading..."
    else:
        cardpic = 'curl -O http://magiccards.info/scans/en/'+cardloc[1]+'/'+cardloc[3]+'jpg'
        os.system(cardpic)
        #card scans are labeled via set number -> need to rename the file temporarily to avoid potential overwriting until decklist is finalized
        rename = 'mv '+cardloc[3]+'jpg Scans/'+localname
        os.system(rename)

    img = Image.open('Scans/'+localname)

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

    lookupCMC = './Scans/'+name2+'_'+set+'_cmc.png'

    if lookupCMC in storedCMCs:

        print "Card CMC' already been used, loading..."
        tap0 = Image.open(lookupCMC)
        
        if tap0.mode != 'RGBA':
            tap0 = tap0.convert('RGBA')

        cmc.paste(tap0, (0,0), mask=tap0)

        #still need to check cost adjustment...
        for n in range(len(cost)-1):
            if (cost[n] == '1') and (check9.find(cost[n+1]) != -1):
                adjustcmc = 1
        
    else:
        
        for n in range(len(cost)-1):

            #reset the large mana cost markers
            if greaterthan9 == 1:
                greaterthan9 = 0
                adjustcmc = 1
                continue

            #lands have no mana cost and are tagged with '*'
            if cost[n] == "*":
                continue

            else:
                if (cost[n] == '1') and (check9.find(cost[n+1]) != -1):
                    finalcost = cost[n]+cost[n+1]
                    greaterthan9 = 1
                else:
                    finalcost = cost[n]

                symbol = 'Mana/Mana_'+finalcost+'.png'

                tap0 = Image.open(symbol)
                if tap0.mode != 'RGBA':
                    tap0 = tap0.convert('RGBA')

                tap = tap0.resize((16,16))

                cmc.paste(tap, (15*n,0), mask=tap)

        cmc.save('Scans/'+name2+'_'+set+'_cmc.png')

    #place the cropped picture of the current card
    deck.paste(cut, (0,34*nstep))
    
    #adjust cmc size to reflex manacost greater than 9
    if adjustcmc == 1:
        deck.paste(cmc, (280-15*(len(cost)-1),8+34*nstep), mask=cmc)
        adjustcmc = 0
    else:
        deck.paste(cmc, (280-15*len(cost),8+34*nstep), mask=cmc)

#    os.system('rm -r '+name2+'.jpg')
#    if cost[n] != "*":
#        os.system('rm -r '+name2+'.png')
#        os.system('rm -r '+name2+'_cmc.png')

    nstep = nstep+1

decklist.close()

deck = deck.crop((0, 0, deckwidth-10, deckheight))

#deck.save("deck.png")
deck.save(str(sys.argv[1])[0:-4]+".png")
