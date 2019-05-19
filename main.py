import RPi.GPIO as GPIO

from DataBase import DataBase
from Bell import Bell

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21,GPIO.OUT)
    GPIO.output(21,GPIO.HIGH)

    MONGO_DB = "test_database"
    MONGO_USER = "deva"
    MONGO_PASS = "pragati@123"

    db = DataBase(MONGO_DB, MONGO_USER, MONGO_PASS)
    myBell = Bell(db)
    myBell.start()
except KeyboardInterrupt:
    GPIO.cleanup()
