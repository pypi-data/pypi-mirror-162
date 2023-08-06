"""
WiP
"""

from gidapptools.meta_data.interface import setup_meta_data, get_meta_info, get_meta_item, get_meta_paths
from gidapptools.gid_logger.logger import setup_main_logger, get_logger, setup_main_logger_with_file_logging, get_main_logger, get_handlers


__version__ = "0.3.2"


from pathlib import Path
import logging

THIS_FILE_DIR = Path(__file__).resolve().parent
log = logging.getLogger(THIS_FILE_DIR.parent.name)


from tzlocal import reload_localzone

reload_localzone()
