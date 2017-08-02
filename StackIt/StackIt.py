#!/usr/bin/env python
import os
import sys

import builder
import config

if __name__ == "__main__":
    config.settingsfile = 'settings.yml'

    if len(sys.argv) == 1:
        import GUIapp
        GUIapp.main()
    else:
        if sys.argv[1] == '--automatedtest':
            import glob
            for deck in glob.glob('testdecks/*.txt'):
                builder.main(deck)
            for deck in glob.glob('testdecks/*.de[ck]'):
                builder.main(deck)
        elif os.path.isdir(sys.argv[1]):
            import watcher
            watcher.main(sys.argv[1])
        else:
            builder.main(sys.argv[1])
