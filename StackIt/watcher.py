import os, shutil, sys, time
from StackIt import builder

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def islist(event):
    return not event.is_directory and not os.path.splitext(event.src_path)[1] == ".png"

class StackItEventHandler(FileSystemEventHandler):

    def on_moved(self, event):
        pass

    def on_created(self, event):
        # self.on_modified(self, event)
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        print(event.src_path)
        if islist(event):
            time.sleep(1)
            static_scroll = self.static_img[:-4] + "-scroll.png"
            if os.path.exists(self.static_img):
                os.remove(self.static_img)
            if os.path.exists(static_scroll):
                os.remove(static_scroll)

            try:
                res = builder.main(event.src_path)
                shutil.copyfile(res, self.static_img)
                shutil.copyfile(res[:-4] + "-scroll.png", static_scroll)
            except Exception as e:
                print(e)


def main(path):
    print('Watching {0} for decks'.format(path))
    event_handler = StackItEventHandler()
    event_handler.static_img = os.path.join(path, 'StackIt.png')
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
