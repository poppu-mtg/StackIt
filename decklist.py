import os, sys
import mmap

#XML parsing
import xml.etree.ElementTree

#HTML parsing
from lxml import html
import requests

import scraper, config
from globals import Card, List

MTG = 1
POKEMON = 2
HEX = 3

def parse_list(decklist):
    # Magic by default
    game = MTG
    ncount = 0
    isSideboard = False

    mainboard = []
    sideboard = []
    commander = []

    isDeckXML = mmap.mmap(decklist.fileno(), 0, access=mmap.ACCESS_READ)
    if isDeckXML.find('xml') != -1:
        print('decklist is in MTGO XML format')
        decklist = preprocess_xml(decklist)

    for raw_line in decklist:
        line = raw_line.strip().replace('\t', ' ')
        if len(line) == 0:
            if game == MTG:
                isSideboard = True
            continue

        # Identify game
        if line[0] in ['#', '*']:
            if line.lower().find('* pok') != -1:
                print('Decklist is for Pokemon TCGO ...')
                game = POKEMON
                isSideboard = False
            continue

        if line.lower().find('champion:') != -1 or line.lower().find('mercenary:') != -1:
            print('Decklist is for Hex TCG')
            game = HEX
            #Hex TCG specific variables
            HexChampion = {}
            HexMercenary = {}
            HexCards = {}
            listChampions = open(os.path.join('.', 'HexLists', 'HexList-Champion.dat'), 'r')
            for l in listChampions:
                HexChampion[l.split('.jpg')[1].strip()] = l.split('.jpg ')[0]
            listChampions.close()

            listMercenaries = open(os.path.join('.', 'HexLists', 'HexList-Mercenary.dat'), 'r')
            for l in listMercenaries:
                HexMercenary[l.split('.jpg')[1].strip()] = l.split('.jpg ')[0]
            listMercenaries.close()

            listCards = open(os.path.join('.', 'HexLists', 'HexList-AllCards.dat'), 'r')
            for l in listCards:
                HexCards[l.split('.jpg')[1].strip()] = l.split('.jpg ')[0]
            listCards.close()

            data = line.split(':')
            cmdr = data[1].strip()
            if data[0].lower() == 'champion':
                commander.append(Card(name=cmdr, quantity=1, collector_num=HexChampion[cmdr], set="C", cost=None))
            else:
                commander.append(Card(name=cmdr, quantity=1, collector_num=HexMercenary[cmdr], set="M", cost=None))
            continue

        if game == HEX:
            if line.lower() in ['', 'troops', 'spells', 'resources', 'reserves']:
                if line.lower() == 'reserves':
                    isSideboard = True
                    continue
                else:
                    continue
            else:
                data = line.split('x ', 1)
                quantity = data[0]
                name = data[1].strip()
                guid = HexCards[name]
                card = Card(name=name, quantity=quantity, collector_num=guid, set=None, cost=None)
                if isSideboard:
                    sideboard.append(card)
                else:
                    mainboard.append(card)
        elif game == MTG:
            quantity, name = line.split(' ', 1)
            card = scraper.get_card_info(name, quantity)
            if isSideboard:
                sideboard.append(card)
            else:
                mainboard.append(card)
        elif game == POKEMON:
            if line[0].isdigit():
                data = line.split(' ')

                quantity = data[0]
                set = data[-2]
                setID = data[-1]
                name = data[1]+' '

                for item in data[2:-2]:
                    name += item + ' '
                mainboard.append(Card(name=name, set=set, quantity=quantity, collector_num=setID, cost=None))

        ncount = ncount + 1

    return List(game, mainboard, sideboard, commander)

def preprocess_xml(decklist):
    '''Converts an XML (.dec) mtgo decklist into a standard decklist'''
    info = xml.etree.ElementTree.parse(str(sys.argv[1])).getroot()
    mainboard = {}
    sideboard = {}

    for atype in info.findall('Cards'):
        if atype.get('Sideboard') == "true":
            if atype.get('Name') in sideboard:
                sideboard[atype.get('Name')] += int(atype.get('Quantity'))
            else:
                sideboard[atype.get('Name')] = int(atype.get('Quantity'))
        else:
            if atype.get('Name') in mainboard:
                mainboard[atype.get('Name')] += int(atype.get('Quantity'))
            else:
                mainboard[atype.get('Name')] = int(atype.get('Quantity'))

    decklist = []
    for card in mainboard.keys():
        decklist.append('{n} {c}'.format(n=mainboard[card], c=card.replace(' / ', ' // ')))
    decklist.append('')
    for card in sideboard.keys():
        decklist.append('{n} {c}'.format(n=sideboard[card], c=card.replace(' / ', ' // ')))
    return decklist
