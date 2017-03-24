import collections, os

# Named Tuple that defines the attribues of a card.
Card = collections.namedtuple('Card', ['name', 'set', 'cost', 'quantity', 'collector_num'])

List = collections.namedtuple('List', ['game', 'mainboard', 'sideboard', 'commander'])

#create a dictionary for non-basic mana:
specmana = {
    '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '10': '10',
    '11': '11', '12': '12', '13': '13', '14': '14', '15': '15', '16': '16', 
    'X': 'X', 'C': 'C', 'W': 'W', 'U': 'U', 'B': 'B', 'R': 'R', 'G': 'G', 
    'W/P': 'P', 'U/P': 'Q', 'B/P': 'S', 'R/P': 'T', 'G/P': 'V', 
    '2/W': 'Y', '2/U': 'Z', '2/B': '@', '2/R': 'A', '2/G': 'D', 
    'W/U': 'E', 'U/B': 'F', 'B/R': 'H', 'R/G': 'I', 'G/W': 'J', 'W/B': 'K', 'U/R': 'L', 'B/G': 'M', 'R/W': 'N', 'G/U': 'O'
    }

#create a list of reprint sets:
mtgreprints = ['MMA','MM2','MM3','EMA','TPR','CHR','MD1']

SCAN_PATH = os.path.join('.', 'cache', 'Scans')
CMC_PATH = os.path.join('.', 'cache', 'manacosts')

def mkcachepaths():
    if not os.path.exists('./cache'):
        os.mkdir('./cache')
    if not os.path.exists(SCAN_PATH):
        os.mkdir(SCAN_PATH)
    if not os.path.exists(CMC_PATH):
        os.mkdir(CMC_PATH)

