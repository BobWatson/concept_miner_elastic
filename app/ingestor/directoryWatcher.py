from pathlib import Path
import os
import threading
import logging

from ingestor.contentProcessor import contentProcessor

class directoryWatcher:
    def __init__(self, watch_folder):
        self.watch_folder = watch_folder
        self.contentProcessor = contentProcessor()
        self.content_extractors = {}
        self.running = False
        self.event = threading.Event()
        
    def run(self, timer):
        if self.running is True:
            return
        
        logging.info(f"directoryWatcher watching {self.watch_folder}")
        
        self.main_thread = threading.Thread(target=self._run,args=[timer])
        self.main_thread.start()
        
    def stop(self):
        self.event.set()
            
    def _run(self, timer):
        self.running = True
        
        while not self.event.is_set():
            self.refresh_files()
            self.event.wait(timer)
            
        self.event.clear()
        self.running = False
        
    def refresh_files(self):
        fileList = [x for x in Path(self.watch_folder).rglob('*.*')]
        for file in fileList:
            file_tup = os.path.splitext(file)
            ext = file_tup[1][1::]
            if ext in self.content_extractors:
                try:
                    content = self.content_extractors[ext](file)
                except:
                    logging.error(f"Failed to extract file: {file}")
                self.contentProcessor.process(file=file, body=content, timestamp=os.stat(file).st_ctime)
            else:
                logging.warning(f"No handler for '{ext}', file: {file}")
        return
                
    def add_handler(self, type, handler):
        self.content_extractors[type] = handler
        return