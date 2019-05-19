import Helper as h
from Relay import relay_off, relay_on
from datetime import datetime
import time

PIN = 21


class Bell:
    def __init__(self, db):
        self.db = db
        self.midNight = datetime.strptime("00:00:00", "%H:%M:%S")
        self.checkCurrentSchedule()
        self.isDayChecked = list(self.db.config.find({},{"isDayChecked":1,"_id":0}))[0]["isDayChecked"]
        self.isHoliday = list(self.db.config.find({},{"isHoliday":1,"_id":0}))[0]["isHoliday"]
        self.defaultList = h.toTimeList(list(self.db.defaultSchedule.find({},{"_id":0,"time":1})))
        print(self.isDayChecked)
        self.updateSchedule()

    def start(self):
        relay_off(PIN)
        while True:
            currentTime = datetime.now().time().replace(microsecond=0)
            self.checkDay(currentTime)
            self.longBells = h.toTimeList(list(self.db.longBells.find({},{"_id":0,"time":1})))

            if self.isHoliday:
                time.sleep(1)
                continue
            self.updateSchedule()
            timeList, statusList = h.ScheduleToLists(self.schedule)
            modList  = self.getModList(timeList)
            #print(timeList,":stat",statusList)
            if self.checkForTurn(currentTime, timeList, statusList,modList):
                self.ring(currentTime)
                if currentTime not in self.defaultList:
                	self.db.logDetails.insert({"Date": datetime.now().strftime("%d-%m-%Y"),"time":currentTime.strftime("%H:%M:%S")})

    def ring(self, currentTime):
        delay = 3
        if currentTime in self.longBells:
            delay = 5
            if currentTime not in self.defaultList:
                self.db.longBells.remove({"time": currentTime.strftime("%H:%M:%S")})
        relay_on(PIN)
        print("Relay ON")
        time.sleep(delay)
        relay_off(PIN)
        print("Relay OFF")
        self.syncWithdb(currentTime)

    def updateSchedule(self):
        self.schedule = h.getSchedule(self.db.currentSchedule)
       
    def getModList(self, timeList):
        modList = []
        for ele in timeList:
            modList.append(ele.replace(second = ele.second + 1))
            modList.append(ele.replace(second = ele.second + 2))
            modList.append(ele.replace(second = ele.second + 3))
        modList = sorted(modList)
        return modList


    def checkForTurn(self, currentTime, timeList, statusList, modList):
        if currentTime in timeList or currentTime in modList:
            index = timeList.index(currentTime.replace(second = 0))
            if statusList[index] == "Not Rang":
                return True

    def syncWithdb(self, time):
        time.replace(second = 0)
        time = time.strftime("%H:%M:%S")
        self.db.currentSchedule.update(
            {"time": time}, {"$set": {"status": "Completed"}})
        self.updateSchedule()
        
    def syncDayCheck(self):
        self.db.config.update({},{ "$set": {"isDayChecked":self.isDayChecked}})
       
    def syncHoliday(self):
        self.db.config.update({},{ "$set": {"isHoliday":self.isHoliday}})

    def checkCurrentSchedule(self):
        if len(list(self.db.currentSchedule.find())) == 0:
            self.restoreToDefault();
            
                
    def restoreToDefault(self):
        for item in self.db.defaultSchedule.find({}, {"_id": 0, "tag": 0}):
            self.db.currentSchedule.insert(item)
            self.db.currentSchedule.update(
                {}, {"$set": {"status": "Not Rang"}}, multi=True)
        

    def getMidNightList(self):
        flag0 = datetime.time(self.midNight)
        flag1 = datetime.time(self.midNight.replace(second = 1))
        flag2 = datetime.time(self.midNight.replace(second = 2))
        flag3 = datetime.time(self.midNight.replace(second = 3))
        return [flag0,flag1,flag2,flag3]

    def checkDay(self, currentTime):
        if currentTime in self.getMidNightList():
            self.isDayChecked = False
            self.syncDayCheck()
        if not self.isDayChecked:
            self.db.currentSchedule.drop()
            self.restoreToDefault();
            day = datetime.today().weekday()
            holidayList = h.getHolidayList(list(self.db.holidayData.find({}, {"Date": 1, "_id": 0})))
            if day==6 or datetime.now().date() in holidayList:
                self.isHoliday = True
                self.syncHoliday()
                print("Holiday!!")

            else:
                self.isHoliday = False
                self.syncHoliday()
            self.isDayChecked = True
            self.syncDayCheck()

