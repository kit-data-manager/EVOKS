from Skosmos.skosmos import Skosmos
from evoks.settings import SKOSMOS_DEV_DIR

skosmos_dev = Skosmos(SKOSMOS_DEV_DIR)

skosmos_live = Skosmos('skosmos-live/config.ttl')
