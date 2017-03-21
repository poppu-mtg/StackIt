import os, yaml

SETTINGS = dict()

if not os.path.exists('settings.yml'):
    with open('settings.yml', 'w') as f:
        f.write("""
cards:
  plains: uh
  island: uh
  swamp: uh
  mountain: uh
  forest: uh
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
