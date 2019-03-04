import os, cv2, datetime
from . import credentials

# Directories
DATA_DIR = os.path.join(os.getcwd(), 'data')
TEMPLATES_DIR = os.path.join(DATA_DIR, 'templates')
DIAGRAMS_DIR = os.path.join(DATA_DIR, 'diagrams')
ERROR_DIR = os.path.join(DATA_DIR, 'error')
DEBUG_DIR = os.path.join(DATA_DIR, 'debug')
TMP_DIR = os.path.join('/tmp', 'MemesAnalyser')

# Files
IMG_EXT = ".jpg"
DATABASE_NAME = 'database.madb'
DATABASE_PATH = os.path.join(DATA_DIR, DATABASE_NAME)
TMP_DATABASE_PATH = os.path.join(TMP_DIR, DATABASE_NAME)
DATABASE_TABLES = {'templates': {"ID": 'INTEGER PRIMARY KEY', "name": 'TEXT', "level_correction": 'INTEGER', "counts": 'INTEGER', "date": 'INTEGER', "date2": 'INTEGER', "threshold": 'INTEGER',
                                 "search_name": 'TEXT'},
                   'matches': {"source_ID": 'INT',
                               "ID": 'TEXT UNIQUE',
                               "template_ID": 'INTEGER',
                               "match_ccoeff": 'INTEGER', 'scale_ccoeff': 'INTEGER', 'position_x_ccoeff': 'INTEGER', 'position_y_ccoeff': 'INTEGER',
                               "match_ccorr": 'INTEGER', 'scale_ccorr': 'INTEGER', 'position_x_ccorr': 'INTEGER', 'position_y_ccorr': 'INTEGER',
                               "match_sqdiff": 'INTEGER', 'scale_sqdiff': 'INTEGER', 'position_x_sqdiff': 'INTEGER', 'position_y_sqdiff': 'INTEGER',
                               "match": 'INTEGER',
                               "score": 'INTEGER',
                               'time': 'INTEGER'
                               },
                   'sources': {"ID": 'INTEGER PRIMARY KEY', "site": 'TEXT', "type": 'TEXT', "value": 'TEXT', "name": 'TEXT', "language": 'TEXT', "last_time": 'INTEGER', "counts": 'INTEGER'}

                   }
TIME_STAMP = "%Y_%m_%d_%H:%M:%S"

# Multiprocessing
PIPES = {'subprocess': 0, 'memes': 96, 'download': 24, 'database': 50}
PIPE_RETRY_DELAY = 0.5
DOWNLOADERS_NUMBER = 16
ANALYSERS_NUMBER = 48
EXIT_TIMEOUT = 60

# Downloading
MAX_RETIRES = 3
DOWNLOAD_TIMEOUT = 20
SCORE_THRESHOLD = 5
HASHTAG_SCORE_THRESHOLD = 100
TIME_THRESHOLD = datetime.timedelta(7)
TIME_BATCH_SIZE = 86400  # 1 day
REDDIT_CREDENTIALS = credentials.REDDIT_CREDENTIALS
INSTAGRAM_CREDENTIALS = credentials.INSTAGRAM_CREDENTIALS

# Analysis
MAX_LEVEL = 8
MIN_LEVEL = 3
MIN_SCALE = 6
MAX_SCALE = 12
SCALE_STEPS = 8
MARGIN_PERC = 0.2

PRIMARY_SEARCH_LEVEL = 5
SECONDARY_SEARCH_LEVEL = 8
FIRST_SELECTION_NUMBER = 10

MATCH_TEMPLATE_METHODS = ((cv2.TM_CCOEFF_NORMED, 0, 0.29, 'ccoeff'), (cv2.TM_CCORR_NORMED, 0, 0.49, 'ccorr'), (cv2.TM_SQDIFF_NORMED, 1, 0.22, 'sqdiff'))
METHODS_NUMBER = len(MATCH_TEMPLATE_METHODS)

# Database
DIGITS = 4
TIME_BETWEEN_BACKUPS = 60
