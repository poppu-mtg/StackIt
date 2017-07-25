import os, yaml
import globals

SETTINGS = dict()
DEFAULTS = yaml.load("""
cards:
  plains: unh
  island: unh
  swamp: unh
  mountain: unh
  forest: unh
options:
  display_sideboard: yes
  indent_hex_title: no
fonts:
  mtg: belerensmallcaps-bold-webfont.ttf
  pkmn: ufonts.com_humanist521bt-ultrabold-opentype.otf
  hex: Arial Bold.ttf
""")

def init():
    global SETTINGS
    if not os.path.exists(os.path.join(globals.globaldir, 'settings.yml')):
        SETTINGS = DEFAULTS
        Save()

    with open('settings.yml') as f:
        SETTINGS = yaml.load(f)
        if SETTINGS is None:
            # File exists, but is empty
            SETTINGS = DEFAULTS
            Save()

    for group in DEFAULTS.keys():
        if group not in SETTINGS.keys():
            SETTINGS[group] = DEFAULTS[group]
            Save()

    print("==Settings==")
    print(yaml.dump(SETTINGS))

def Get(group, name):
    try:
        return SETTINGS[group][name]
    except KeyError:
        try:
            SETTINGS[group][name] = DEFAULTS[group][name]
            Save()
            return SETTINGS[group][name]
        except KeyError:
            return None

def Save():
    with open('settings.yml', 'w') as f:
        f.write(yaml.dump(SETTINGS, default_flow_style=False))

init()
