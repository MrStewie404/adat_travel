import logging
import os


class CustomLogFileHandler(logging.FileHandler):
    def __init__(self, filename, **kwargs):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(filename, **kwargs)
