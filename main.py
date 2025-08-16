import sys
import logging
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from services import settings_service, logging_service

# Load settings and setup logging as early as possible
app_settings = settings_service.load_settings()
logging_service.setup_logging(app_settings.log)

# Get a logger for this module
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Application starting...")
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
    logger.info("Application finished.")