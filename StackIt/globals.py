import collections, os, sys
from os import path
import appdirs

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
mtgreprints = ['MMA', 'MM2', 'MM3', 'EMA', 'TPR', 'CHR', 'MD1']

setmappings = {'mps': 'mpskld', 'unh': 'uh'}

aftermath = [
    'Dusk // Dawn', 'Commit // Memory', 'Never // Return', 'Insult // Injury', 'Mouth // Feed', 'Start // Finish',
    'Reduce // Rubble', 'Destined // Lead', 'Onward // Victory', 'Spring // Mind', 'Prepare // Fight', 'Failure // Comply',
    'Rags // Riches', 'Cut // Ribbons', 'Heaven // Earth'
]

# pyinstaller
if getattr(sys, 'frozen', False):
    print('Using Bundled Python')
    localdir = sys._MEIPASS
    globaldir = os.path.dirname(sys.executable)
    bundled = True
else:
    print('Running on python ' + sys.version)
    localdir = path.abspath(path.dirname(__file__))
    globaldir = appdirs.user_data_dir('StackIt')
    bundled = False

PY3 = sys.version_info > (3, 0)

# print("DIR={0}".format(localdir))
CACHE_PATH = appdirs.user_cache_dir('StackIt')
RESOURCES_PATH = os.path.join(localdir, 'resources')

SCAN_PATH = os.path.join(CACHE_PATH, 'Scans')
CMC_PATH = os.path.join(CACHE_PATH, 'manacosts')

def mkcachepaths():
    if not os.path.exists(globaldir):
        os.makedirs(globaldir)
    if not os.path.exists(CACHE_PATH):
        os.mkdir(CACHE_PATH)
    if not os.path.exists(SCAN_PATH):
        os.mkdir(SCAN_PATH)
    if not os.path.exists(CMC_PATH):
        os.mkdir(CMC_PATH)

mkcachepaths()
