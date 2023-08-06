import logging
from .util import green

__name__ = green('[Primer]')

logging.basicConfig(
    level=logging.INFO,
    format=__name__ + " * [%(asctime)s - %(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

