import os, sys

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

import scraper, config, decklist
from globals import Card, specmana

#ensure that mana costs greater than 9 (Kozilek, Emrakul...) aren't misaligned

def GenerateCMC(name, cost):
    check9 = '0123456'
    adjustcmc = False
    cmc = Image.new('RGBA',(16*len(cost), 16))
    diskcost = cost.strip().replace('*', '_').replace('/','-')
    # lookupCMC = os.path.join('CmcCache', '{cost}.png'.format(cost=diskcost))
    lookupCMC = os.path.join('CmcCache', '{cost}.png'.format(cost=diskcost))
    if os.path.exists(lookupCMC):
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
            #add correct treatment of separation for split cards
            elif cost[n] == '/':
                symbol = 'Mana/Mana_spn.png'
                tap0 = Image.open(symbol)
                if tap0.mode != 'RGBA':
                    tap0 = tap0.convert('RGBA')

                tap = tap0.resize((16, 16))
                cmc.paste(tap, (15 * n, 0), mask=tap)
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

                tap = tap0.resize((16, 16))
                cmc.paste(tap, (15 * n, 0), mask=tap)
        cmc.save(lookupCMC)
    return cmc, adjustcmc

def draw_hex_card(name, guid, quantity, nstep):
    lookupScan = scraper.download_scanHex(name, guid)
    
    img = Image.open(lookupScan)
    img = img.crop((39,130,309,164))

    #resize the gradient to the size of im...
    alpha = gradient.resize(img.size)

    #put alpha in the alpha band of im...
    img.putalpha(alpha)

    bkgd = Image.new("RGB", img.size, "black")
    bkgd.paste(img, (0,0), mask=img)

    cut = bkgd

    draw = ImageDraw.Draw(cut)
    #create text outline
    draw.text((6, 6),str(quantity)+'  '+name,(0,0,0), font=hexfnt)
    draw.text((8, 6),str(quantity)+'  '+name,(0,0,0), font=hexfnt)
    draw.text((6, 8),str(quantity)+'  '+name,(0,0,0), font=hexfnt)
    draw.text((8, 8),str(quantity)+'  '+name,(0,0,0), font=hexfnt)
    #enter text
    draw.text((7, 7),str(quantity)+'  '+name,(250,250,250), font=hexfnt)

    deck.paste(cut, (50,35*nstep))

def draw_mtg_card(name, expansion, quantity, cost, nstep):
    if name.find(" // ") != -1:
        namesplit = name.replace(" // ", "/")
        lookupScan = scraper.download_scan(namesplit, expansion)
    else:
        lookupScan = scraper.download_scan(name, expansion)

    #    print name, lookupScan

    img = Image.open(lookupScan)
    if name.find(" // ") != -1:
        img = img.rotate(-90)

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

    cmc, adjustcmc = GenerateCMC(name, cost)

    #place the cropped picture of the current card
    deck.paste(cut, (0, 34 * nstep))

    #adjust cmc size to reflex manacost greater than 9
    if adjustcmc:
        deck.paste(cmc, (280-15*(len(cost)-1),8+34*nstep), mask=cmc)
        adjustcmc = False
    else:
        deck.paste(cmc, (280-15*len(cost),8+34*nstep), mask=cmc)

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

xtopPKMN = 8
xbotPKMN = 237
ytopPKMN = 11.5
ybotPKMN = 45.25

#load the MTG text fonts
fnt = ImageFont.truetype("beleren-webfonts/belerensmallcaps-bold-webfont.ttf", 14)
fnt_title = ImageFont.truetype("beleren-webfonts/belerensmallcaps-bold-webfont.ttf", 18)

#load the PKMN text fonts
pokefnt = ImageFont.truetype("humanist-webfonts/ufonts.com_humanist521bt-ultrabold-opentype.otf", 10)

pokefnt_title = ImageFont.truetype("humanist-webfonts/ufonts.com_humanist521bt-ultrabold-opentype.otf", 14)

hexfnt = ImageFont.truetype("agane-webfonts/Agane-55-roman.ttf", 14)
hexfnt_title = ImageFont.truetype("agane-webfonts/Agane-55-roman.ttf", 16)

# create a horizontal gradient...
Hexgradient = Image.new('L', (1,255))

#map the gradient
for x in range(64):
    Hexgradient.putpixel((0,x),254)
for x in range(64):
    Hexgradient.putpixel((0,64+x),254-x)
for x in range(128):
    Hexgradient.putpixel((0,127+x),190-int(1.5*x))

# create a horizontal gradient...
gradient = Image.new('L', (255, 1))

#map the gradient
#for x in range(64):
#    gradient.putpixel((x,0),254)
#for x in range(64):
#    gradient.putpixel((63+x,0),max(254-x,0))
#for x in range(128):
#    gradient.putpixel((127+x,0),max(int(190-1.5*x),0))
for x in range(128):
    gradient.putpixel((x, 0), int(1.5 * x))
for x in range(64):
    gradient.putpixel((127 + x, 0), 190 + x)
for x in range(64):
    gradient.putpixel((190 + x, 0), 254)

#check if we should include the sideboard
if len(sys.argv) == 2:
    doSideboard = config.Get('options', 'display_sideboard')
else:
    if str(sys.argv[2]) in ['sb', 'sideboard']:
        doSideboard = True
    elif str(sys.argv[2]) in ['nosb']:
        doSideboard = False
    else:
        doSideboard = config.Get('options', 'display_sideboard')

#open user input decklist
raw_decklist = open(str(sys.argv[1]), 'r')

canonical_decklist = decklist.parse_list(raw_decklist)

raw_decklist.close()

print(repr(canonical_decklist))

# create a header with the deck's name
if canonical_decklist.game == decklist.MTG:
    title = Image.new("RGB", (280, 34), "black")
    drawtitle = ImageDraw.Draw(title)
    drawtitle.text((10, 7), os.path.basename(str(sys.argv[1]))[0:-4], (250, 250, 250), font=fnt_title)
elif canonical_decklist.game == decklist.POKEMON:
    title = Image.new("RGB", (219, 35), "black")
    drawtitle = ImageDraw.Draw(title)
    drawtitle.text((10, 8), os.path.basename(str(sys.argv[1]))[0:-4],(250, 250, 250), font=pokefnt_title)
elif canonical_decklist.game == decklist.HEX:
    title = Image.new("RGB", (320,34), "black")
    nametitle = str(sys.argv[1])[0:-4]
    nshard = 0
    for shard in ['[DIAMOND]', '[SAPPHIRE]', '[BLOOD]', '[RUBY]', '[WILD]']:
        #print nametitle,nshard
        if nametitle.find(shard) != -1:
            nametitle = nametitle.replace(shard,'')
            newshard = Image.open(os.path.join('.','Mana',shard+'.png')).resize((20,20))
            title.paste(newshard,(10+nshard*20,7))
            nshard = nshard + 1
    drawtitle = ImageDraw.Draw(title)
    drawtitle.text((15 + nshard * 20, 12), os.path.basename(nametitle), (250, 250, 250), font=hexfnt_title)

ncountMB = len(canonical_decklist.mainboard)
ncountSB = len(canonical_decklist.sideboard)
ncount = ncountMB
if ncountSB == 0:
    doSideboard = False
if doSideboard:
    #create a Sideboard partition
    sideboard = Image.new("RGB", (280, 34), "black")
    drawtitle = ImageDraw.Draw(sideboard)
    sideboard_name = "Sideboard"
    if canonical_decklist.game == decklist.HEX:
        sideboard_name = "Reserves"
    drawtitle.text((10, 7), sideboard_name, (250, 250, 250), font=fnt_title)
    ncount += ncountSB + 1

#define the size of the canvas, incl. space for the title header
if canonical_decklist.game == decklist.MTG:
    deckwidth = 280
    deckheight = 34*(ncount+1)
elif canonical_decklist.game == decklist.POKEMON:
    deckwidth = 219
    deckheight = 35*(ncount+1)
elif canonical_decklist.game == decklist.HEX:
    deckwidth = 320
    deckheight = 35*(ncount+1)

#reset the sideboard marker
isSideboard = 0

deck = Image.new("RGB", (deckwidth, deckheight), "white")

deck.paste(title, (0,0))

#now read the decklist
if canonical_decklist.game == decklist.MTG:
        lands = {}

        for card in canonical_decklist.mainboard:
            #this step checks whether a specific art is requested by the user - provided via the set name
            quantity = canonical_decklist.mainboard[card]
            card = scraper.get_card_info(card, quantity)
            if card is None:
                continue

            if card.cost == "*\n":
                lands[card] = quantity
                continue
            draw_mtg_card(card.name, card.set, card.quantity, card.cost, nstep)
            nstep = nstep + 1

        for card in lands:
            draw_mtg_card(card.name, card.set, card.quantity, card.cost, nstep)
            nstep = nstep + 1

        if doSideboard:
            deck.paste(sideboard, (0,34*nstep))
            nstep = nstep + 1
            for card in canonical_decklist.sideboard:
                quantity = canonical_decklist.sideboard[card]
                card = scraper.get_card_info(card, quantity)
                if card is None:
                    continue
                draw_mtg_card(card.name, card.set, card.quantity, card.cost, nstep)
                nstep = nstep + 1

elif canonical_decklist.game == decklist.POKEMON:
    for card in canonical_decklist.mainboard:
            card = canonical_decklist.mainboard[card]
            quantity = card.quantity
            lookupScan, displayname = scraper.download_scanPKMN(card.name, card.set, card.collector_num)
            
            img = Image.open(lookupScan)

            #check if im has Alpha band...
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            #resize the gradient to the size of im...
            alpha = gradient.resize(img.size)

            #put alpha in the alpha band of im...
            img.putalpha(alpha)

            bkgd = Image.new("RGB", img.size, "black")
            bkgd.paste(img, (0, 0), mask=img)

            cut = bkgd.crop((xtopPKMN, ytopPKMN+90, xbotPKMN-10, ybotPKMN+100))
            cut = cut.resize((deckwidth,34))

            draw = ImageDraw.Draw(cut)
            #create text outline
            draw.text((6, 11), str(quantity) + '  ' + displayname, (0, 0, 0), font=pokefnt)
            draw.text((8, 11), str(quantity) + '  ' + displayname, (0, 0, 0), font=pokefnt)
            draw.text((6, 13), str(quantity) + '  ' + displayname, (0, 0, 0), font=pokefnt)
            draw.text((8, 13), str(quantity) + '  ' + displayname, (0, 0, 0), font=pokefnt)
            #enter text
            draw.text((7, 12), str(quantity) + '  ' + displayname, (250, 250, 250), font=pokefnt)

            #place the cropped picture of the current card
            deck.paste(cut, (0, 35 * nstep))

            nstep = nstep+1

elif canonical_decklist.game == decklist.HEX:
    banner = Image.new("RGB", (deckheight-35, 50), "black")
    if len(canonical_decklist.commander) > 0:
        cmdr, guid = canonical_decklist.commander.keys()[0].split(' / ')
        typeCM = canonical_decklist.commander.values()[0]

        drawbanner = ImageDraw.Draw(banner)
        drawbanner.text((15,15), str(cmdr), (250,250,250), font=hexfnt_title)

        lookupScan = scraper.download_scanHexCM(cmdr, guid, typeCM)

        mainguyImg = Image.open(lookupScan)
        mainguycut = mainguyImg.crop((135,55,185,275))

        banner = banner.rotate(90, expand=True)

        #check if im has Alpha band...
        if mainguycut.mode != 'RGBA':
            mainguycut = mainguycut.convert('RGBA')

        #resize the gradient to the size of im...
        alpha = Hexgradient.resize(mainguycut.size)

        #put alpha in the alpha band of im...
        mainguycut.putalpha(alpha)

        banner.paste(mainguycut, (0,0), mask=mainguycut)

        deck.paste(banner, (0,35))

    for card in canonical_decklist.mainboard:
        name, guid = card.split(' / ')
        quantity = canonical_decklist.mainboard[card]

        draw_hex_card(name, guid, quantity, nstep)
        nstep = nstep + 1
    if doSideboard:
        deck.paste(sideboard, (50,35*nstep))
        nstep = nstep + 1
        for card in canonical_decklist.sideboard:
            name, guid = card.split(' / ')
            quantity = canonical_decklist.sideboard[card]

            draw_hex_card(name, guid, quantity, nstep)
            nstep = nstep + 1
            
if canonical_decklist.game == decklist.MTG:
    deck = deck.crop((0, 0, deckwidth - 10, deckheight))
elif canonical_decklist.game == decklist.POKEMON:
    deck = deck.crop((0, 0, deckwidth - 10, 35 * nstep))
elif canonical_decklist.game == decklist.HEX:
    deck = deck.crop((0, 0, deckwidth-22, deckheight))
    
deck.save(str(sys.argv[1])[0:-4] + ".png")
altpath = config.Get('options', 'output_path')
if altpath is not None:
    deck.save(altpath)
