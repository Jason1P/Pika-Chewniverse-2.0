import logging
import configparser
import os
import shutil
from datetime import datetime
from pathlib import Path


config = configparser.ConfigParser()
config.read('config.ini')
logging_info = config['LOGGING']

def log(logginglevel, message, packet=""):
    debug_mode = True
    debug_levels = [LOGGINGLEVEL.DEBUG, LOGGINGLEVEL.AUTHDEBUG, LOGGINGLEVEL.WORLDDEBUG, LOGGINGLEVEL.WORLDDEBUGROUTE, LOGGINGLEVEL.REPLICADEBUG, LOGGINGLEVEL.CHARACTERDEBUG, LOGGINGLEVEL.GAMEMESSAGE]

    if debug_mode is False:
        if logginglevel in debug_levels:
            pass
        else:
            print(u"" + logginglevel + LOGGINGLEVEL.PACKET + packet + LOGGINGLEVEL.MESSAGE + message)
    else:
        print(u"" + logginglevel + LOGGINGLEVEL.PACKET + packet + LOGGINGLEVEL.MESSAGE + message)
    
    if logging_info['LogOutput'] == "True":
        logging.basicConfig(level=logging.INFO, filename='pikachewniverse.log')
        logging.debug("" + LOGGINGLEVEL.PACKET + packet + LOGGINGLEVEL.MESSAGE + message)
    else:
        pass

def logmanage():
    if os.path.exists("Logs"):
        dir = (str(Path.cwd()) + '\\Logs')
        if (len([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))])) > 19:
            try:
                shutil.rmtree('Logs')
                os.mkdir('Logs')
            except:
                pass
        else:
            pass
        if os.path.exists("Logs"):
            pass
        else:
            os.chdir("Logs")
        if os.path.exists("pikachewniverse.log"):
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
            shutil.move((str(Path.cwd()) + r"\pikachewniverse.log"), (str(Path.cwd()) + "\Logs\\"))
            os.rename((str(Path.cwd()) + r"\Logs\pikachewniverse.log"),(str(Path.cwd()) + "\Logs\\" + dt_string + ".log"))
        else:
            pass
    else:
        os.mkdir("Logs")

class LOGGINGLEVEL:
    WARNING = '\u001b[33m[WARNING]'
    ERROR = '\u001b[31m[ERROR]'
    DEBUG = '\u001b[34m[DEBUG]'
    AUTHDEBUG = '\u001b[32m[DEBUG][AUTH]'
    WORLDDEBUG = '\u001b[34m[DEBUG][WORLD]'
    WORLDDEBUGROUTE = '\u001b[34m[WORLD][ROUTE]'
    REPLICADEBUG = '\u001b[34m[DEBUG][REPLICA]'
    CHARACTERDEBUG = '\u001b[30m[DEBUG][CHARACTER]'

    AUTH = '\u001b[32m[AUTH]'
    WORLD = '\u001b[34m[WORLD]'
    REPLICA = '\u001b[34m[REPLICA]'
    CHARACTER = '\u001b[30m[CHARACTER]'

    GAMEMESSAGE = '\u001b[36m[GAMEMESSAGE]'
    PACKET = '\u001b[37m'
    MESSAGE = '\u001b[35;1m'
    INFO = '\u001b[36m[INFO]'

