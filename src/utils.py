import logging
def setup_logging(level: str = 'INFO'):
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    logging.getLogger().setLevel(level)
