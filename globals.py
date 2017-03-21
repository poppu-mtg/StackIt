import collections

# Named Tuple that defines the attribues of a card.
Card = collections.namedtuple('Card', ['name', 'set', 'cost', 'quantity', 'collector_num'])

List = collections.namedtuple('List', ['game', 'mainboard', 'sideboard', 'commander'])

#create a dictionary for non-basic mana:
specmana = {'0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '10': '10', '11': '11', '12': '12', '13': '13', '14': '14', '15': '15', '16': '16', 'X': 'X', 'C': 'C', 'W': 'W', 'U': 'U', 'B': 'B', 'R': 'R', 'G': 'G', 'PW': 'P', 'PU': 'Q', 'PB': 'S', 'PR': 'T', 'PG': 'V', '2W': 'Y', '2U': 'Z', '2B': '@', '2R': 'A', '2G': 'D', 'WU': 'E', 'UB': 'F', 'BR': 'H', 'RG': 'I', 'GW': 'J', 'WB': 'K', 'UR': 'L', 'BG': 'M', 'RW': 'N', 'GU': 'O'}

