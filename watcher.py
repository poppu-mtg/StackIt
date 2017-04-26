import os, sys, time
import StackIt

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class StackItEventHandler(FileSystemEventHandler):
    def islist(self, event):
        return not event.is_directory and not os.path.splitext(event.src_path)[1] == ".png"

    def on_moved(self, event):
        pass

    def on_created(self, event):
        print(event.src_path)
        if self.islist(event):
            time.sleep(1)
            try:
                StackIt.main(event.src_path)
            except Exception as e:
                print(e)

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        print(event.src_path)
        if self.islist(event):
            time.sleep(1)
            try:
                StackIt.main(event.src_path)
            except Exception as e:
                print(e)


def main(path):
    print('Watching {0} for decks'.format(path))
    event_handler = StackItEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    main(path)
