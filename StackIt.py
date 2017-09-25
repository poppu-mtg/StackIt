#!/usr/bin/env python
import os
import sys
import glob

try:
    from StackIt import builder, config, watcher
except ImportError:
    import builder, config, watcher

if __name__ == "__main__":
    config.settingsfile = 'settings.yml'

    if len(sys.argv) == 1:
        try:
            from StackIt import GUIapp
        except ImportError:
            import GUIapp
        GUIapp.main()
    else:
        if sys.argv[1] == '--automatedtest':
            for deck in glob.glob('testdecks/*.txt'):
                builder.main(deck)
            for deck in glob.glob('testdecks/*.de[ck]'):
                builder.main(deck)
            try:
                from StackIt import GUIapp
            except ImportError:
                import GUIapp
            GUIapp.main()
        elif os.path.isdir(sys.argv[1]):
            watcher.main(sys.argv[1])
        else:
            builder.main(sys.argv[1])
