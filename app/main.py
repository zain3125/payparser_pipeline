import time
from watchdog.observers import Observer
from watcher import ImageHandler
from config import WATCH_FOLDER

def main():
    print(f"Starting to watch folder: {WATCH_FOLDER}")
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_FOLDER, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping watcher...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
