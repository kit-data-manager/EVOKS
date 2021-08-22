from Fuseki.fuseki import Fuseki
from evoks.settings import FUSEKI_DEV_HOST, FUSEKI_LIVE_HOST, FUSEKI_PORT, FUSEKI_DEV_BACKUP_PATH, FUSEKI_LIVE_BACKUP_PATH

# TODO: Dont hardcode, get the values from the config file
fuseki_dev = Fuseki(FUSEKI_DEV_HOST, FUSEKI_PORT,
                    'development', FUSEKI_DEV_BACKUP_PATH)

fuseki_live = Fuseki(FUSEKI_LIVE_HOST, FUSEKI_PORT,
                     'production', FUSEKI_LIVE_BACKUP_PATH)
