from logging import getLogger, basicConfig, DEBUG

from api.ui import MainWindow, GMenu

logger = getLogger(__name__)
basicConfig(level=DEBUG)

MainWindow().add_menu(GMenu("TEST"))
logger.debug("TEEEST ADDON")