from flask import Flask,jsonify,request
import pymongo
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)

CORS(app)
MONGO_HOST = "192.168.137.24"
MONGO_PORT = 27017
MONGO_DB = "test_database"
MONGO_USER = "deva"
MONGO_PASS = "pragati@123"

CORS(app, resources={r"/*": {"origins": "*"}})

con = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
db = con[MONGO_DB]

currentSchedule = db.currentSchedule
defaultSchedule = db.defaultSchedule
logDetails = db.alertBellLog
holidayData = db.holidayData

def getListFromCollection(mylist):
    stringList = list(map(lambda x: x["time"],mylist))
    return stringList

def getReasonFromCollection(mylist):
    stringList = list(map(lambda x: x["reason"],mylist))
    return stringList

def getHolidayFromCollection(mylist):
    holidayList = list(map(lambda x: x["Date"],mylist))
    return holidayList

@app.route("/currentSchedule",methods = ['GET'])
def getCurrentSchedule():
    output = []
    for entry in currentSchedule.find():
        output.append({ "time": entry['time']})
    tempOutput = sorted(output, key = lambda val: val["time"])
    return jsonify({"result": tempOutput})

@app.route("/handleEndBell", methods = ['POST'])
def handleEndBell():
    data = request.form
    currentScheduleList = getListFromCollection(list(currentSchedule.find({},{ "time":1,"_id": 0})))
    temp = list(currentSchedule.find({},{ "reason":1,"_id": 0}))
    if len(temp) is not 0:
        reasonList = getReasonFromCollection(list(currentSchedule.find({},{ "reason":1,"_id": 0})))
        print(reasonList)
        print("hi")
        if '1' in reasonList:
            result = {"myStatus":"No Bell can be set after End Bell"}
            return jsonify(result)
    if data["time"] in currentScheduleList:
        print("Time already exist")
        result = {"myStatus":"Time already present in currentSchedule"}
        return jsonify(result)
    else:
        myresult = {"time": data["time"], "reason": '1', "myStatus":"Succesfully updated in database"}
        result = myresult.copy()
        currentSchedule.insert_one(myresult)
        return jsonify(result)

@app.route('/handleMiddleBell', methods=['POST'])
def handleMiddleBell():
    print('hello')
    data = request.form
    currentScheduleList = getListFromCollection(list(currentSchedule.find({},{ "time":1,"_id": 0})))
    if data["time"] in currentScheduleList:
        print("Time already exist")
        result = {"myStatus":"Time already present in currentSchedule"}
        return jsonify(result)
    else:
        myresult = {"time": data["time"], "myStatus":"Succesfully updated in database"}
        newresult = {"time": data["extraTime"], "myStatus":"Succesfully updated in database",}
        result = myresult.copy()
        currentSchedule.insert_one(myresult)
        if data['extraTime'] in currentScheduleList:
            result['myStatus'] = "Time already present in currentSchedule"
        currentSchedule.insert_one(newresult)
        return jsonify(result)

@app.route('/handleExtraBell', methods=['POST'])
def handleExtraBell():
    print('hi')
    data = request.form
    currentScheduleList = getListFromCollection(list(currentSchedule.find({},{ "time":1,"_id": 0})))
    if data["time"] in currentScheduleList:
        print("Time already exist")
        result = {"myStatus":"Time already present in currentSchedule"}
        return jsonify(result)
    else:
        myresult = {"time": data["time"], "myStatus":"Succesfully updated in database"}
        result = myresult.copy()
        currentSchedule.insert_one(myresult)
        return jsonify(result)

@app.route("/logDetails",methods = ['GET'])
def getLogDetails():
    output = []
    for entry in logDetails.find():
        output.append({ "time": entry['time'], "reason":entry['reason']})
    return jsonify({"result": output})

@app.route("/holidayList", methods = ['GET'])
def getHolidays():
    output = []
    for entry in holidayData.find():
        output.append({"date": entry['Date']})
    return jsonify({"result": output})

@app.route("/addHoliday", methods=['POST'])
def addHoliday():
    data = request.form
    holidayList = getHolidayFromCollection(list(holidayData.find({},{ "Date":1,"_id": 0})))
    if data["date"] in holidayList:
        print("Date already present in holiday list")
        result = {"myStatus" : "Date already present in holiday list"}
        return jsonify(result)
    else:
        myresult = {'Date': data['date'],'myStatus':"Successfully updated in holiday list"}
        result = myresult.copy()
        print(myresult)
        holidayData.insert_one(myresult)
        return jsonify(result)

@app.route('/deleteHoliday',methods=['POST'])
def deleteHoliday():
    data = request.form
    myresult = {'Date':data['date']}
    result = myresult.copy()
    holidayData.remove(myresult)
    return jsonify(result)

@app.route("/clearSchedule", methods = ['GET'])
def clearSchedule():
    currentSchedule.drop()
    return 'cleared schedule'

@app.route("/RestoreDefaults", methods = ['GET'])
def restoreDefaults():
    currentSchedule.drop()
    for entry in defaultSchedule.find():
        currentSchedule.insert({"time": entry['time']})
    return 'restored to defaults'
    
if __name__ == "__main__":
    app.run()    
