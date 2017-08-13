import os, sys, re

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

from StackIt import scraper, config, decklist, globals
from StackIt.globals import Card, specmana, aftermath

#ensure that mana costs greater than 9 (Kozilek, Emrakul...) aren't misaligned

FILTER = Image.LANCZOS

# Sizes
INNER_MTG_MANA_COST_IMAGE_SIZE = 15
OUTER_MTG_MANA_COST_IMAGE_SIZE = 16
HEX_MANA_COST_IMAGE_SIZE = 20
INNER_ENTRY_HEIGHT = 34
OUTER_ENTRY_HEIGHT = 35
DECK_WIDTH = 280
HEX_DECK_WIDTH = 219
HEX_MASTER_DECK_WIDTH = 320
SCROLLING_DECK_WIDTH_ADJUSTMENT = 10
SCROLLING_DECK_WIDTH = DECK_WIDTH - SCROLLING_DECK_WIDTH_ADJUSTMENT

# Image Positioning
HEX_MANA_COST_LEFT = 10
HEX_MANA_COST_TOP = 7
HEX_MANA_COST_SIZE = 20
HEX_BANNER_TOP = 50
SIDEBOARD_LEFT = 50
MTG_CMC_OFFSET_TOP = 8

# Crops
HEX_IMAGE_CROP = (39, 130, 309, 164)
HEX_MAINGUY_CROP = (134, 55, 185, 275)
MTG_BACKGROUND_X_TOP_OFFSET = 12
MTG_BACKGROUND_Y_OFFSET = 125
MTG_BACKGROUND_Y_OFFSET_AFTERMATH = 55
POKEMON_BACKGROUND_OFFSET_Y_TOP = 90
POKEMON_BACKGROUND_OFFSET_X_BOTTOM = 10
POKEMON_BACKGROUND_OFFSET_Y_BOTTOM = 100
MTG_WIDTH_CROP_RIGHT = 10
POKEMON_WIDTH_CROP_RIGHT = 10
HEX_WIDTH_CROP_RIGHT = 22

# Colors
BLACK = (0, 0, 0)
NEARLY_WHITE = (250, 250, 250)
RGB_MAX_0 = 255
RGB_MAX_1 = 256
HALF = int(RGB_MAX_1 / 2)
BAD_HALF = int(RGB_MAX_0 / 2)
QUARTER = int(RGB_MAX_1 / 4)
BAD_THREE_QUARTERS = 190

# Text Positioning
TEXT_LEFT, TEXT_TOP = 7, 7
POKEMON_TEXT_LEFT, POKEMON_TEXT_TOP = 7, 12
MTG_TITLE_POSITION = (10, 7)
POKEMON_TITLE_POSITION = (10, 8)
TEXT_PASTE_LEFT = 50
HEX_TITLE_LEFT = 15
HEX_TITLE_TOP = 12
SIDEBOARD_TITLE_POSITION = (10, 7)
HEX_BANNER_POSITION = (15, 15)

if config.Get('options', 'indent_hex_title'):
    TITLE_INDENT = TEXT_PASTE_LEFT
else:
    TITLE_INDENT = 0

# Type Sizes
MTG_FONT_SIZE = 14
MTG_TITLE_FONT_SIZE = 18
HEX_FONT_SIZE = 16
HEX_TITLE_FONT_SIZE = 18
POKEMON_FONT_SIZE = 10
POKEMON_TITLE_FONT_SIZE = 14

# Rotation
ROTATE_RIGHT = 90
ROTATE_LEFT = -90

#some position initialization
X_TOP = 8
X_BOTTOM = 304
Y_TOP = 11.5
Y_BOTTOM = 45.25

X_TOP_POKEMON = 8
X_BOTTOM_POKEMON = 237
Y_TOP_POKEMON = 11.5
Y_BOTTOM_POKEMON = 45.25

def GenerateCMC(name, cost):
    check9 = '0123456'
    adjustcmc = False
    cmc = Image.new('RGBA', (OUTER_MTG_MANA_COST_IMAGE_SIZE * len(cost), OUTER_MTG_MANA_COST_IMAGE_SIZE))
    diskcost = cost.strip().replace('*', '_').replace('/', '-')
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

                tap = tap0.resize((OUTER_MTG_MANA_COST_IMAGE_SIZE, OUTER_MTG_MANA_COST_IMAGE_SIZE), FILTER)
                cmc.paste(tap, (INNER_MTG_MANA_COST_IMAGE_SIZE * n, 0), mask=tap)
            else:
                if (len(cost) > n + 1) and (cost[n] == '1') and (check9.find(cost[ n+ 1]) != -1):
                    finalcost = cost[n] + cost[n + 1]
                    greaterthan9 = True
                else:
                    finalcost = cost[n]
                symbol = os.path.join(globals.RESOURCES_PATH, 'mana', 'Mana_' + finalcost + '.png')

                tap0 = Image.open(symbol)
                if tap0.mode != 'RGBA':
                    tap0 = tap0.convert('RGBA')

                tap = tap0.resize((OUTER_MTG_MANA_COST_IMAGE_SIZE, OUTER_MTG_MANA_COST_IMAGE_SIZE), FILTER)
                cmc.paste(tap, (INNER_MTG_MANA_COST_IMAGE_SIZE * n, 0), mask=tap)
        cmc.save(lookupCMC)
    return cmc, adjustcmc

def draw_hex_card(name, guid, quantity, nstep):
    lookupScan = scraper.download_scanHex(name, guid)

    img = Image.open(lookupScan)
    img = img.crop(HEX_IMAGE_CROP)

    #resize the gradient to the size of im...
    alpha = gradient.resize(img.size, FILTER)

    #put alpha in the alpha band of im...
    img.putalpha(alpha)

    bkgd = Image.new("RGB", img.size, "black")
    bkgd.paste(img, (0, 0), mask=img)

    cut = bkgd

    draw = ImageDraw.Draw(cut)
    #create text outline
    text = str(quantity) + '  ' + name
    draw.text((TEXT_LEFT - 1, TEXT_TOP - 1), text, BLACK, font=fnt)
    draw.text((TEXT_LEFT + 1, TEXT_TOP - 1), text, BLACK, font=fnt)
    draw.text((TEXT_LEFT - 1, TEXT_TOP + 1), text, BLACK, font=fnt)
    draw.text((TEXT_LEFT + 1, TEXT_TOP + 1), text, BLACK, font=fnt)
    #enter text
    draw.text((TEXT_LEFT, TEXT_TOP), text, NEARLY_WHITE, font=fnt)

    deck.paste(cut, (TEXT_PASTE_LEFT, (OUTER_ENTRY_HEIGHT) * nstep))

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
        img = img.rotate(ROTATE_LEFT)

    #check if im has Alpha band...
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    #resize the gradient to the size of im...
    alpha = gradient.resize(img.size, FILTER)

    #put alpha in the alpha band of im...
    img.putalpha(alpha)

    bkgd = Image.new("RGB", img.size, "black")
    bkgd.paste(img, (0, 0), mask=img)

    if isAftermath == True:
        cut = bkgd.crop((X_TOP + MTG_BACKGROUND_X_TOP_OFFSET, Y_TOP + MTG_BACKGROUND_Y_OFFSET_AFTERMATH, X_BOTTOM, Y_BOTTOM + MTG_BACKGROUND_Y_OFFSET_AFTERMATH))
    else:
        cut = bkgd.crop((X_TOP + MTG_BACKGROUND_X_TOP_OFFSET, Y_TOP + MTG_BACKGROUND_Y_OFFSET, X_BOTTOM, Y_BOTTOM + MTG_BACKGROUND_Y_OFFSET))

    draw = ImageDraw.Draw(cut)
    text = str(card.quantity) + '  ' + card.name
    #create text outline
    draw.text((TEXT_LEFT - 1, TEXT_TOP - 1), text, BLACK, font=fnt)
    draw.text((TEXT_LEFT + 1, TEXT_TOP - 1), text, BLACK, font=fnt)
    draw.text((TEXT_LEFT - 1, TEXT_TOP + 1), text, BLACK, font=fnt)
    draw.text((TEXT_LEFT + 1, TEXT_TOP + 1), text, BLACK, font=fnt)
    #enter text
    draw.text((TEXT_LEFT, TEXT_TOP), text, NEARLY_WHITE, font=fnt)

    cmc, adjustcmc = GenerateCMC(card.name, card.cost)

    #place the cropped picture of the current card
    deck.paste(cut, (0, INNER_ENTRY_HEIGHT * nstep))
    #for scrolling decklist
    tmpwidth, tmpheight = cut.size
    cut2 = cut.crop((0, 0, tmpwidth - SCROLLING_DECK_WIDTH_ADJUSTMENT, tmpheight))
    deck2.paste(cut2, (SCROLLING_DECK_WIDTH * nstep, 0))

    #adjust cmc size to reflex manacost greater than 9
    if adjustcmc:
        deck.paste(cmc, (DECK_WIDTH - INNER_MTG_MANA_COST_IMAGE_SIZE * len(card.cost), MTG_CMC_OFFSET_TOP + INNER_ENTRY_HEIGHT * nstep), mask=cmc)
        #for scrolling decklist
        deck2.paste(cmc, (SCROLLING_DECK_WIDTH * (nstep + 1) - INNER_MTG_MANA_COST_IMAGE_SIZE * len(card.cost), MTG_CMC_OFFSET_TOP), mask=cmc)
        adjustcmc = False
    else:
        deck.paste(cmc, (DECK_WIDTH - INNER_MTG_MANA_COST_IMAGE_SIZE * (len(card.cost) + 1), MTG_CMC_OFFSET_TOP + INNER_ENTRY_HEIGHT * nstep), mask=cmc)
        #for scrolling decklist
        deck2.paste(cmc, (SCROLLING_DECK_WIDTH * (nstep + 1) - INNER_MTG_MANA_COST_IMAGE_SIZE * (len(card.cost) + 1), MTG_CMC_OFFSET_TOP), mask=cmc)

globals.mkcachepaths()

# create a horizontal gradient...
Hexgradient = Image.new('L', (1, RGB_MAX_0))

#map the gradient
for x in range(QUARTER):
    Hexgradient.putpixel((0, x), RGB_MAX_0)
for x in range(QUARTER):
    Hexgradient.putpixel((0, QUARTER + x), RGB_MAX_0 - x)
for x in range(HALF):
    Hexgradient.putpixel((0, BAD_HALF + x), BAD_THREE_QUARTERS - int(1.5 * x))

# create a horizontal gradient...
gradient = Image.new('L', (RGB_MAX_0, 1))

#map the gradient
for x in range(HALF):
    gradient.putpixel((x, 0), int(1.5 * x))
for x in range(QUARTER):
    gradient.putpixel((BAD_HALF + x, 0), BAD_THREE_QUARTERS + x)
for x in range(QUARTER):
    gradient.putpixel((BAD_THREE_QUARTERS + x, 0), RGB_MAX_0 - 1)

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
        fnt = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', config.Get('fonts', 'mtg')), MTG_FONT_SIZE)
        fnt_title = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', config.Get('fonts', 'mtg')), MTG_TITLE_FONT_SIZE)
        title = Image.new("RGB", (DECK_WIDTH, INNER_ENTRY_HEIGHT), "black")
        drawtitle = ImageDraw.Draw(title)
        drawtitle.text(MTG_TITLE_POSITION, os.path.basename(str(filename))[0:-4], NEARLY_WHITE, font=fnt_title)
    elif deck_list.game == decklist.POKEMON:
        fnt = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', config.Get('fonts', 'pkmn')), POKEMON_FONT_SIZE)
        fnt_title = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', config.Get('fonts', 'pkmn')), POKEMON_TITLE_FONT_SIZE)
        title = Image.new("RGB", (HEX_DECK_WIDTH, OUTER_ENTRY_HEIGHT), "black")
        drawtitle = ImageDraw.Draw(title)
        drawtitle.text(POKEMON_TITLE_POSITION, os.path.basename(str(filename))[0:-4], NEARLY_WHITE, font=fnt_title)
    elif deck_list.game == decklist.HEX:
        fnt = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', config.Get('fonts', 'hex')), HEX_FONT_SIZE)
        fnt_title = ImageFont.truetype(os.path.join(globals.RESOURCES_PATH, 'fonts', config.Get('fonts', 'hex')), HEX_TITLE_FONT_SIZE)
        title = Image.new("RGB", (HEX_MASTER_DECK_WIDTH, INNER_ENTRY_HEIGHT), "black")
        nametitle = str(filename)[0:-4]
        nshard = 0
        for re_match in re.finditer(r'(\[[^\]]*\])', nametitle):
            shard = re_match.group(0)
            if nametitle.find(shard) != -1:
                nametitle = nametitle.replace(shard, '')
                newshard = Image.open(os.path.join(globals.RESOURCES_PATH, 'hexicons', shard + '.png')).resize((HEX_MANA_COST_IMAGE_SIZE, HEX_MANA_COST_IMAGE_SIZE), FILTER)
                title.paste(newshard, (TITLE_INDENT + HEX_MANA_COST_LEFT + nshard * HEX_MANA_COST_SIZE, HEX_MANA_COST_TOP))
                nshard = nshard + 1
        drawtitle = ImageDraw.Draw(title)
        drawtitle.text((TITLE_INDENT + HEX_TITLE_LEFT + nshard * HEX_MANA_COST_IMAGE_SIZE, HEX_TITLE_TOP), os.path.basename(nametitle), NEARLY_WHITE, font=fnt_title)

    ncountMB = len(deck_list.mainboard)
    ncountSB = len(deck_list.sideboard)
    ncount = ncountMB
    if ncountSB == 0:
        doSideboard = False
    if doSideboard:
        #create a Sideboard partition
        sideboard = Image.new("RGB", (DECK_WIDTH, INNER_ENTRY_HEIGHT), "black")
        drawtitle = ImageDraw.Draw(sideboard)
        sideboard_name = "Sideboard"
        if deck_list.game == decklist.HEX:
            sideboard_name = "Reserves"
        drawtitle.text(SIDEBOARD_TITLE_POSITION, sideboard_name, NEARLY_WHITE, font=fnt_title)
        ncount += ncountSB + 1

    #define the size of the canvas, incl. space for the title header
    if deck_list.game == decklist.MTG:
        deckwidth = DECK_WIDTH
        deckheight = INNER_ENTRY_HEIGHT * (ncount + 1)
        #for scrolling decklist
        deckwidth2 = SCROLLING_DECK_WIDTH * (ncount + 1)
        deckheight2 = INNER_ENTRY_HEIGHT
    elif deck_list.game == decklist.POKEMON:
        deckwidth = HEX_DECK_WIDTH
        deckheight = OUTER_ENTRY_HEIGHT * (ncount + 1)
        deckwidth2 = SCROLLING_DECK_WIDTH * (ncount + 1)
        deckheight2 = INNER_ENTRY_HEIGHT
    elif deck_list.game == decklist.HEX:
        deckwidth = HEX_MASTER_DECK_WIDTH
        deckheight = OUTER_ENTRY_HEIGHT * (ncount + 1)
        deckwidth2 = SCROLLING_DECK_WIDTH * (ncount + 1)
        deckheight2 = INNER_ENTRY_HEIGHT

    #reset the sideboard marker
    isSideboard = 0

    global deck
    deck = Image.new("RGB", (deckwidth, deckheight), "white")
    #for scrolling decklist
    global deck2
    deck2 = Image.new("RGB", (deckwidth2, deckheight2), "white")

    deck.paste(title, (0, 0))
    #for scrolling decklist
    title2 = title.crop((0, 0, SCROLLING_DECK_WIDTH, INNER_ENTRY_HEIGHT))
    deck2.paste(title2, (0, 0))

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
                deck.paste(sideboard, (0, INNER_ENTRY_HEIGHT * nstep))
                #for scrolling decklist
                sideboard2 = sideboard.crop((0, 0, SCROLLING_DECK_WIDTH, INNER_ENTRY_HEIGHT))
                deck2.paste(sideboard2, (SCROLLING_DECK_WIDTH * nstep, 0))
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
                alpha = gradient.resize(img.size, FILTER)

                #put alpha in the alpha band of im...
                img.putalpha(alpha)

                bkgd = Image.new("RGB", img.size, "black")
                bkgd.paste(img, (0, 0), mask=img)

                cut = bkgd.crop((X_TOP_POKEMON, Y_TOP_POKEMON + POKEMON_BACKGROUND_OFFSET_Y_TOP, X_BOTTOM_POKEMON - POKEMON_BACKGROUND_OFFSET_X_BOTTOM, Y_BOTTOM_POKEMON + POKEMON_BACKGROUND_OFFSET_Y_BOTTOM))
                cut = cut.resize((deckwidth, INNER_ENTRY_HEIGHT))

                draw = ImageDraw.Draw(cut)
                #create text outline
                text = str(quantity) + '  ' + displayname
                draw.text((POKEMON_TEXT_LEFT - 1, POKEMON_TEXT_TOP - 1), text, BLACK, font=fnt)
                draw.text((POKEMON_TEXT_LEFT + 1, POKEMON_TEXT_TOP - 1), text, BLACK, font=fnt)
                draw.text((POKEMON_TEXT_LEFT - 1, POKEMON_TEXT_TOP + 1), text, BLACK, font=fnt)
                draw.text((POKEMON_TEXT_LEFT + 1, POKEMON_TEXT_TOP + 1), text, BLACK, font=fnt)
                #enter text
                draw.text((POKEMON_TEXT_LEFT, POKEMON_TEXT_TOP), text, NEARLY_WHITE, font=fnt)

                #place the cropped picture of the current card
                deck.paste(cut, (0, OUTER_ENTRY_HEIGHT * nstep))

                nstep = nstep + 1

    elif deck_list.game == decklist.HEX:
        banner = Image.new("RGB", (deckheight - OUTER_ENTRY_HEIGHT, HEX_BANNER_TOP), "black")
        if len(deck_list.commander) > 0:
            cmdr = deck_list.commander[0]
            guid = cmdr.collector_num
            typeCM = cmdr.set

            drawbanner = ImageDraw.Draw(banner)
            drawbanner.text(HEX_BANNER_POSITION, str(cmdr.name), NEARLY_WHITE, font=fnt_title)

            lookupScan = scraper.download_scanHexCM(cmdr.name, guid, typeCM)

            mainguyImg = Image.open(lookupScan)
            mainguycut = mainguyImg.crop(HEX_MAINGUY_CROP)

            banner = banner.rotate(ROTATE_RIGHT, expand=True)

            #check if im has Alpha band...
            if mainguycut.mode != 'RGBA':
                mainguycut = mainguycut.convert('RGBA')

            #resize the gradient to the size of im...
            alpha = Hexgradient.resize(mainguycut.size, FILTER)

            #put alpha in the alpha band of im...
            mainguycut.putalpha(alpha)

            banner.paste(mainguycut, (0, 0), mask=mainguycut)

            deck.paste(banner, (0, OUTER_ENTRY_HEIGHT))

        for card in deck_list.mainboard:
            draw_hex_card(card.name, card.collector_num, card.quantity, nstep)
            nstep = nstep + 1

        if doSideboard:
            deck.paste(sideboard, (SIDEBOARD_LEFT, OUTER_ENTRY_HEIGHT * nstep))
            nstep = nstep + 1
            for card in deck_list.sideboard:
                draw_hex_card(card.name, card.collector_num, card.quantity, nstep)
                nstep = nstep + 1

    if deck_list.game == decklist.MTG:
        deck = deck.crop((0, 0, deckwidth - MTG_WIDTH_CROP_RIGHT, deckheight))
        deck2 = deck2.crop((0, 0, deckwidth2, deckheight2 - 2))
    elif deck_list.game == decklist.POKEMON:
        deck = deck.crop((0, 0, deckwidth - POKEMON_WIDTH_CROP_RIGHT, OUTER_ENTRY_HEIGHT * nstep))
    elif deck_list.game == decklist.HEX:
        deck = deck.crop((0, 0, deckwidth - HEX_WIDTH_CROP_RIGHT, deckheight))

    output_path = str(filename)[0:-4] + ".png"
    deck.save(output_path)
    #for scrolling decklist
    output_path2 = str(filename)[0:-4] + "-scroll.png"
    deck2.save(output_path2)
    altpath = config.Get('options', 'output_path')
    if altpath is not None:
        deck.save(altpath)
    return output_path
