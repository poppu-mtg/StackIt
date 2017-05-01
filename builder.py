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

import scraper, config, decklist, globals
from globals import Card, specmana, aftermath

#ensure that mana costs greater than 9 (Kozilek, Emrakul...) aren't misaligned

def GenerateCMC(name, cost):
    check9 = '0123456'
    adjustcmc = False
    cmc = Image.new('RGBA',(16 * len(cost), 16))
    diskcost = cost.strip().replace('*', '_').replace('/', '-')
    # lookupCMC = os.path.join('CmcCache', '{cost}.png'.format(cost=diskcost))
    lookupCMC = os.path.join(globals.CMC_PATH, '{cost}.png'.format(cost=diskcost))
    if os.path.exists(lookupCMC):
        tap0 = Image.open(lookupCMC)
        if tap0.mode != 'RGBA':
            tap0 = tap0.convert('RGBA')
        cmc.paste(tap0, (0, 0), mask=tap0)
        #still need to check cost adjustment...
        for n in range(len(cost) - 1):
            if (cost[n] == '1') and (check9.find(cost[n + 1]) != -1):
                adjustcmc = True
    else:
        greaterthan9 = False
        for n in range(len(cost)):
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
                symbol = os.path.join(globals.RESOURCES_PATH, 'mana', 'Mana_spn.png')
                tap0 = Image.open(symbol)
                if tap0.mode != 'RGBA':
                    tap0 = tap0.convert('RGBA')

                tap = tap0.resize((16, 16))
                cmc.paste(tap, (15 * n, 0), mask=tap)
            else:
                if (len(cost) > n + 1) and (cost[n] == '1') and (check9.find(cost[n+1]) != -1):
                    finalcost = cost[n]+cost[n+1]
                    greaterthan9 = True
                else:
                    finalcost = cost[n]
                symbol = os.path.join(globals.RESOURCES_PATH, 'mana', 'Mana_'+finalcost+'.png')

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
    draw.text((6, 6),str(quantity)+'  '+name,(0,0,0), font=fnt)
    draw.text((8, 6),str(quantity)+'  '+name,(0,0,0), font=fnt)
    draw.text((6, 8),str(quantity)+'  '+name,(0,0,0), font=fnt)
    draw.text((8, 8),str(quantity)+'  '+name,(0,0,0), font=fnt)
    #enter text
    draw.text((7, 7),str(quantity)+'  '+name,(250,250,250), font=fnt)

    deck.paste(cut, (50,35*nstep))

def draw_mtg_card(card, nstep):

    isAftermath = False

    if card.name.find(" // ") != -1:
        namesplit = card.name.replace(" // ", "/")
        lookupScan = scraper.download_scan(namesplit, card.set, card.collector_num)
        if card.name in aftermath:
            isAftermath = True
    else:
        lookupScan = scraper.download_scan(card.name, card.set, card.collector_num)

    img = Image.open(lookupScan)
    if (card.name.find(" // ") != -1) and (isAftermath == False): 
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

    if isAftermath == True:
        cut = bkgd.crop((xtop+12, ytop+55, xbot, ybot+55))
    else:
        cut = bkgd.crop((xtop+12, ytop+125, xbot, ybot+125))

    draw = ImageDraw.Draw(cut)
    #create text outline
    draw.text((6, 6), str(card.quantity)+'  '+card.name,(0,0,0), font=fnt)
    draw.text((8, 6), str(card.quantity)+'  '+card.name,(0,0,0), font=fnt)
    draw.text((6, 8), str(card.quantity)+'  '+card.name,(0,0,0), font=fnt)
    draw.text((8, 8), str(card.quantity)+'  '+card.name,(0,0,0), font=fnt)
    #enter text
    draw.text((7, 7), str(card.quantity)+'  '+card.name,(250,250,250), font=fnt)

    cmc, adjustcmc = GenerateCMC(card.name, card.cost)

    #place the cropped picture of the current card
    deck.paste(cut, (0, 34 * nstep))

    #adjust cmc size to reflex manacost greater than 9
    if adjustcmc:
        deck.paste(cmc, (280-15*len(card.cost),8+34*nstep), mask=cmc)
        adjustcmc = False
    else:
        deck.paste(cmc, (280-15*(len(card.cost)+1),8+34*nstep), mask=cmc)

globals.mkcachepaths()

#some position initialization
xtop = 8
xbot = 304
ytop = 11.5
ybot = 45.25

xtopPKMN = 8
xbotPKMN = 237
ytopPKMN = 11.5
ybotPKMN = 45.25

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

def main(filename):
    doSideboard = config.Get('options', 'display_sideboard')

    #open user input decklist
    raw_decklist = open(str(filename), 'r')

    deck_list = decklist.parse_list(raw_decklist)

    raw_decklist.close()

    print(repr(deck_list))

    nstep = 1
    # create a header with the deck's name
    global fnt
    if deck_list.game == decklist.MTG:
        fnt = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', 'belerensmallcaps-bold-webfont.ttf'), 14)
        fnt_title = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', 'belerensmallcaps-bold-webfont.ttf'), 18)
        title = Image.new("RGB", (280, 34), "black")
        drawtitle = ImageDraw.Draw(title)
        drawtitle.text((10, 7), os.path.basename(str(filename))[0:-4], (250, 250, 250), font=fnt_title)
    elif deck_list.game == decklist.POKEMON:
        fnt = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', 'ufonts.com_humanist521bt-ultrabold-opentype.otf'), 10)
        fnt_title = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', 'ufonts.com_humanist521bt-ultrabold-opentype.otf'), 14)
        title = Image.new("RGB", (219, 35), "black")
        drawtitle = ImageDraw.Draw(title)
        drawtitle.text((10, 8), os.path.basename(str(filename))[0:-4],(250, 250, 250), font=fnt_title)
    elif deck_list.game == decklist.HEX:
        fnt = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', 'Arial Bold.ttf'), 16)
        fnt_title = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', 'Arial Bold.ttf'), 18)
        title = Image.new("RGB", (320,34), "black")
        nametitle = str(filename)[0:-4]
        nshard = 0
        for shard in ['[DIAMOND]', '[SAPPHIRE]', '[BLOOD]', '[RUBY]', '[WILD]']:
            #print nametitle,nshard
            if nametitle.find(shard) != -1:
                nametitle = nametitle.replace(shard,'')
                newshard = Image.open(os.path.join(globals.RESOURCES_PATH, 'mana',shard+'.png')).resize((20,20))
                title.paste(newshard,(10+nshard*20,7))
                nshard = nshard + 1
        drawtitle = ImageDraw.Draw(title)
        drawtitle.text((15 + nshard * 20, 12), os.path.basename(nametitle), (250, 250, 250), font=fnt_title)

    ncountMB = len(deck_list.mainboard)
    ncountSB = len(deck_list.sideboard)
    ncount = ncountMB
    if ncountSB == 0:
        doSideboard = False
    if doSideboard:
        #create a Sideboard partition
        sideboard = Image.new("RGB", (280, 34), "black")
        drawtitle = ImageDraw.Draw(sideboard)
        sideboard_name = "Sideboard"
        if deck_list.game == decklist.HEX:
            sideboard_name = "Reserves"
        drawtitle.text((10, 7), sideboard_name, (250, 250, 250), font=fnt_title)
        ncount += ncountSB + 1

    #define the size of the canvas, incl. space for the title header
    if deck_list.game == decklist.MTG:
        deckwidth = 280
        deckheight = 34*(ncount+1)
    elif deck_list.game == decklist.POKEMON:
        deckwidth = 219
        deckheight = 35*(ncount+1)
    elif deck_list.game == decklist.HEX:
        deckwidth = 320
        deckheight = 35*(ncount+1)

    #reset the sideboard marker
    isSideboard = 0
    
    global deck
    deck = Image.new("RGB", (deckwidth, deckheight), "white")

    deck.paste(title, (0,0))

    #now read the decklist
    if deck_list.game == decklist.MTG:
            lands = []

            for card in deck_list.mainboard:
                #this step checks whether a specific art is requested by the user - provided via the set name

                if card.cost == "*":
                    lands.append(card)
                    continue
                draw_mtg_card(card, nstep)
                nstep = nstep + 1

            for card in lands:
                draw_mtg_card(card, nstep)
                nstep = nstep + 1

            if doSideboard:
                deck.paste(sideboard, (0,34*nstep))
                nstep = nstep + 1
                for card in deck_list.sideboard:
                    draw_mtg_card(card, nstep)
                    nstep = nstep + 1

    elif deck_list.game == decklist.POKEMON:
        for card in deck_list.mainboard:
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
                draw.text((6, 11), str(quantity) + '  ' + displayname, (0, 0, 0), font=fnt)
                draw.text((8, 11), str(quantity) + '  ' + displayname, (0, 0, 0), font=fnt)
                draw.text((6, 13), str(quantity) + '  ' + displayname, (0, 0, 0), font=fnt)
                draw.text((8, 13), str(quantity) + '  ' + displayname, (0, 0, 0), font=fnt)
                #enter text
                draw.text((7, 12), str(quantity) + '  ' + displayname, (250, 250, 250), font=fnt)

                #place the cropped picture of the current card
                deck.paste(cut, (0, 35 * nstep))

                nstep = nstep+1

    elif deck_list.game == decklist.HEX:
        banner = Image.new("RGB", (deckheight-35, 50), "black")
        if len(deck_list.commander) > 0:
            cmdr = deck_list.commander[0]
            guid = cmdr.collector_num
            typeCM = cmdr.set

            drawbanner = ImageDraw.Draw(banner)
            drawbanner.text((15,15), str(cmdr.name), (250,250,250), font=fnt_title)

            lookupScan = scraper.download_scanHexCM(cmdr.name, guid, typeCM)

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

        for card in deck_list.mainboard:
            draw_hex_card(card.name, card.collector_num, card.quantity, nstep)
            nstep = nstep + 1

        if doSideboard:
            deck.paste(sideboard, (50,35*nstep))
            nstep = nstep + 1
            for card in deck_list.sideboard:
                draw_hex_card(card.name, card.collector_num, card.quantity, nstep)
                nstep = nstep + 1
                
    if deck_list.game == decklist.MTG:
        deck = deck.crop((0, 0, deckwidth - 10, deckheight))
    elif deck_list.game == decklist.POKEMON:
        deck = deck.crop((0, 0, deckwidth - 10, 35 * nstep))
    elif deck_list.game == decklist.HEX:
        deck = deck.crop((0, 0, deckwidth-22, deckheight))
    
    output_path = str(filename)[0:-4] + ".png"
    deck.save(output_path)
    altpath = config.Get('options', 'output_path')
    if altpath is not None:
        deck.save(altpath)
    return output_path
