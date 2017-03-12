import os, yaml

settings = dict()

if not os.path.exists('settings.yml'):
    with open('settings.yml', 'w') as f:
        f.write("""
cards:
  Plains: uh
  Island: uh
  Swamp: uh
  Mountain: uh
  Forest: uh
options:
  DisplaySideboard: yes
""")

with open('settings.yml') as f:
    settings = yaml.load(f)

print("==Settings==")
print(yaml.dump(settings))
