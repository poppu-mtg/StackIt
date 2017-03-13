import os, yaml

settings = dict()

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
    settings = yaml.load(f)

print("==Settings==")
print(yaml.dump(settings))

def Get(group, name):
    try:
        return settings[group][name]
    except KeyError:
        return None
