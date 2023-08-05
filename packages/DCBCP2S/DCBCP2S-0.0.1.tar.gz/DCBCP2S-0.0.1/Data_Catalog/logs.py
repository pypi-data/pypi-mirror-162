import logging
from datetime import datetime

date = datetime.now().strftime("%d_%m_%Y")


logging.basicConfig(filename=f"C://Users//hp//Documents//Logs//log_{date}",
                    format='%(asctime)s: %(levelname)s: %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p'
                    )

logger=logging.getLogger()
logger.setLevel(logging.DEBUG)



def debug(msg):
    logger.debug(msg)
    
    
def info(msg):
    logger.info(msg)

def warning(msg):
    logger.warning(msg)

def error(msg):
    logger.error(msg)

def critical(msg):
    logger.critical(msg)

