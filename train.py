import logging
import sys

import env_config
from src.models.ResNet50 import train, test, DEVICE

logger = logging.getLogger(__name__)

# CONSTANTS
IS_PRODUCTION = env_config.IS_PRODUCTION
PROGRAM_CONFIG = env_config.PROGRAM_CONFIG
CURRENT_ARCH = PROGRAM_CONFIG['arch']
DATASET = 'yeast_v4'

EPOCHS = 20
global_step = 0
logger.info(f"{PROGRAM_CONFIG['name']} started in {('production' if IS_PRODUCTION else 'development')} mode")
logger.info(f"Current architecture: {CURRENT_ARCH}; current data set: {DATASET}; number of epochs: [{EPOCHS}]")
logger.info(f"running on {DEVICE}; python version: {list(sys.version_info[:2])}")

for i in range(EPOCHS):
    train(i)
    test(i)

logger.info("\n Finished training.")
