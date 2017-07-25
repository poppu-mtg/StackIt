import os, sys

if __name__ == "__main__":
    if (len(sys.argv) == 1):
        import GUIapp
        GUIapp.main()
    else:
        if sys.argv[1] == '--automatedtest':
            import builder
            import glob
            for deck in glob.glob('testdecks/*.txt'):
                builder.main(deck)
            for deck in glob.glob('testdecks/*.de[ck]'):
                builder.main(deck)
        elif os.path.isdir(sys.argv[1]):
            import watcher
            watcher.main(sys.argv[1])
        else:
            import builder
            builder.main(sys.argv[1])
