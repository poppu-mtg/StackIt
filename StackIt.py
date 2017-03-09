import os, sys
import re

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

resetcurl = "rm -r temp"
resetoutput = "rm -r output"

ncount = 0
nstep = 1

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
for x in range(64):
    gradient.putpixel((x,0),254)
for x in range(64):
    gradient.putpixel((63+x,0),max(254-x,0))
for x in range(128):
    gradient.putpixel((127+x,0),max(int(190-1.5*x),0))

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
    
    #necessary for appropriate treatment of the missing mana cost of lands
    isitland = 0
    isitspecland = 0

    if lines[0] == '#':
        continue

    data = lines.split(" / ")

    quantity = int(data[0])
    name = data[1]

    print len(data), data

    #this step checks whether a specific art is requested by the user - provided via the set name

    if data[2] != "\n":
        
        setcost = data[2].split(" ")
        set = re.sub('([A-Z]{1})', r'\1',setcost[0]).lower()
        if setcost[1] == "\n":
            cost = "*\n"
        else:
            cost = setcost[1]

    else:
        
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

            os.system("curl 'http://www.mtgvault.com/cards/search/?q="+cmcsearch+"&searchtype=name' | grep -i 'card info' > tempcmc")

            cmcdata = open('tempcmc', 'r')

            for lines in cmcdata:
        
                if lines.find("Land") != -1:
                    isitspecland = 1
                    continue

                cmc_part1 = lines.split(" {")[1]
                cmc_part2 = cmc_part1.split("}<")[0]
                altcmc = cmc_part2.split("}{")
                altcmc = [specmana[x] for x in altcmc]
                print name,altcmc

            cmcdata.close()

            scankey = "<a href=" + '"' + "/card/" + scansearch + '/'

            os.system("curl 'http://www.mtgvault.com/cards/search/?q="+cmcsearch+"&searchtype=name' | grep -i 'card_image' > tempscan")

            scandata = open('tempscan', 'r')

            for lines in scandata:

                print lines, name
                
                if lines.find('"'+name+'"') != -1:
                    scan_part1 = lines.split(scankey)[1]
                    altscan = str(scan_part1.split('/"')[0]).lower()
                    print altscan

            scandata.close()

            os.system("rm -r tempcmc")
            os.system("rm -r tempscan")
            
            set = altscan
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
    fetch = "grep -i "+'"'+">"+name+'"'+" temp > output"
    setcurl = "curl 'http://magiccards.info/"+set+"/en.html' > temp"

    os.system(setcurl)
    os.system(fetch)

    lookup = open('output', 'r')

    for item in lookup:

        if item.find("href") != -1:
            findit = item.split('"')
            cardloc = findit[1][:-4]
            continue

    #get the jpg file of the card scan
    cardpic = 'curl -O http://magiccards.info/scans/en/'+cardloc.split("/")[1]+'/'+cardloc.split("/")[3]+'jpg'
    os.system(cardpic)

    #card scans are labeled via set number -> need to rename the file temporarily to avoid potential overwriting until decklist is finalized
    name2 = ''.join(e for e in name if e.isalnum())
    localname = name2+'.jpg'
    rename = 'mv '+cardloc.split("/")[3]+'jpg '+localname
    os.system(rename)

    img = Image.open(localname)

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
    draw.text((9, 6),str(quantity)+'  '+name,(0,0,0), font=fnt)
    draw.text((11, 6),str(quantity)+'  '+name,(0,0,0), font=fnt)
    draw.text((9, 8),str(quantity)+'  '+name,(0,0,0), font=fnt)
    draw.text((11, 8),str(quantity)+'  '+name,(0,0,0), font=fnt)
    #enter text
    draw.text((10, 7),str(quantity)+'  '+name,(250,250,250), font=fnt)

    cmc = Image.new('RGBA',(16*len(cost), 16))

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

            cmc.save(name2+"_cmc.png")

    #place the cropped picture of the current card
    deck.paste(cut, (0,34*nstep))
    
    #adjust cmc size to reflex manacost greater than 9
    if adjustcmc == 1:
        deck.paste(cmc, (280-15*(len(cost)-1),8+34*nstep), mask=cmc)
        adjustcmc = 0
    else:
        deck.paste(cmc, (280-15*len(cost),8+34*nstep), mask=cmc)

    os.system('rm -r '+name2+'.jpg')
    if cost[n] != "*":
        os.system('rm -r '+name2+'.png')
        os.system('rm -r '+name2+'_cmc.png')

    nstep = nstep+1

decklist.close()

#deck.save("deck.png")
deck.save(str(sys.argv[1])[0:-4]+".png")

#cleanup step
os.system(resetcurl)
os.system(resetoutput)
