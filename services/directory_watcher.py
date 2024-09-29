import asyncio
import logging
import os
import time
from asyncio import AbstractEventLoop

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from pipeline import select_pipeline_csv


class WatcherHandler(FileSystemEventHandler):
    def __init__(self, loop: AbstractEventLoop):
        self.loop = loop  # Reference to the running event loop

    def on_created(self, event) -> None:
        """
        Extending the FileSystemEventHandler.on_created to run custom logic based on the flat file type
        :param event:
        :return:
        """

        if not event.is_directory:
            if event.src_path.endswith('.csv'):
                logging.info(f"Detected new CSV file: {os.path.basename(event.src_path)}")
                time.sleep(3)   # small delay to allow the file to write to disk correctly
                select_pipeline_csv(event.src_path)

            # TODO: can extend for other flat files

            # TODO: optional to create process to zip and backup item before deletion
            os.remove(event.src_path)


async def watch_folder(
        loop: AbstractEventLoop,
        target_directory: str
) -> None:
    event_handler = WatcherHandler(loop)
    observer = Observer()
    observer.schedule(event_handler, target_directory, recursive=False)

    observer.start()
    logging.info(f"Watching folder: {target_directory}")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
