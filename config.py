import os, yaml
import globals

SETTINGS = dict()

if not os.path.exists(os.path.join(globals.globaldir, 'settings.yml')):
    with open('settings.yml', 'w') as f:
        f.write("""
cards:
  plains: unh
  island: unh
  swamp: unh
  mountain: unh
  forest: unh
options:
  display_sideboard: yes
""")

with open('settings.yml') as f:
    SETTINGS = yaml.load(f)

print("==Settings==")
print(yaml.dump(SETTINGS))

def Get(group, name):
    try:
        return SETTINGS[group][name]
    except KeyError:
        return None
