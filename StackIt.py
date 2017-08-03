#!/usr/bin/env python
import os
import sys
import glob

try:
    from StackIt import builder, config, GUIapp, watcher
except ImportError:
    import builder, config, GUIapp, watcher

if __name__ == "__main__":
    config.settingsfile = 'settings.yml'

    if len(sys.argv) == 1:
        GUIapp.main()
    else:
        if sys.argv[1] == '--automatedtest':
            for deck in glob.glob('testdecks/*.txt'):
                builder.main(deck)
            for deck in glob.glob('testdecks/*.de[ck]'):
                builder.main(deck)
        elif os.path.isdir(sys.argv[1]):
            watcher.main(sys.argv[1])
        else:
            builder.main(sys.argv[1])
