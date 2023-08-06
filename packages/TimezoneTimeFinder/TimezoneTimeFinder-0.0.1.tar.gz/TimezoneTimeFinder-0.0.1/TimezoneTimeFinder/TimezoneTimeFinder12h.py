import pytz
from datetime import datetime
       

zones = ['Africa/Abidjan', 'Africa/Addis_Ababa', 'Europe/London', 'Europe/Stockholm', 'America/Adak', 'America/Anchorage', 'America/Anguilla', 'America/Araguaina', 
    'America/Atikokan', 'America/Belize', 'America/Creston', 'America/Miquelon', 'Antarctica/Casey', 'Antarctica/Davis', 'Antarctica/DumontDUrville', 'Antarctica/Mawson', 
    'Antarctica/McMurdo', 'Antarctica/Vostok', 'Asia/Baku', 'Asia/Brunei', 'Asia/Chita', 'Atlantic/Cape_Verde', 'Pacific/Apia', 'Pacific/Honolulu']

timeOfDay = ["am", "pm"]

##get a list of all timezones where it's a specific time
def getTimezones(time:str, AmPm:str, minuteCheck=True):
    
    listOfTimeZones = []

    ##make sure the input is formated correctly
    if len(time) != 5:
        raise Exception("ERROR: time not formated correctly (##:##)")
    num = 0

    for character in time:
        if num == 2:
            if character != ":":
                raise Exception("ERROR: time not formated correctly (##:##)")
        else:
            if not character.isdigit():
                raise Exception("ERROR: time not formated correctly (##:##)")
        num += 1
    
    theTime = time.split(":")
    minute = theTime[1]
    hour = theTime[0]


    AmPm = AmPm.lower()
    if AmPm in timeOfDay:
        if AmPm == "am":
            if hour == "12":
                hour == "00"
        else:
            hour = int(hour)+12

    
    time = f"{hour}:{minute}"

    ##Make sure that the time is the current time
    if minuteCheck != False:
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%M")
        if not minute == currentTime:
            raise Exception("ERROR: Time is not correct, minutes must match current")
    
    ##check in what timesones the time matches
    if minuteCheck != False:
        for timezone in pytz.common_timezones:
            timezonee = pytz.timezone(timezone)
            currentDateAndTime = datetime.now(timezonee)
            currentTime = currentDateAndTime.strftime("%H:%M")
            if time == currentTime:
                listOfTimeZones.append(timezone)
        return listOfTimeZones
        
    else:
        for timezone in pytz.common_timezones:
            timezonee = pytz.timezone(timezone)
            currentDateAndTime = datetime.now(timezonee)
            currentTime = currentDateAndTime.strftime("%H")
            if str(hour) == currentTime:
                listOfTimeZones.append(timezone)
        return listOfTimeZones
            





##get a single timezone where it's a specific times
def getTimezone(time:str, AmPm:str, minuteCheck=True):
    

    ##make sure the input is formated correctly
    if len(time) != 5:
        raise Exception("ERROR: time not formated correctly (##:##)")
    num = 0
    for character in time:
        if num == 2:
            if character != ":":
                raise Exception("ERROR: time not formated correctly (##:##)")
        else:
            if not character.isdigit():
                raise Exception("ERROR: time not formated correctly (##:##)")
        num += 1
    
    theTime = time.split(":")
    minute = theTime[1]
    hour = theTime[0]

    AmPm = AmPm.lower()
    if AmPm in timeOfDay:
        if AmPm == "am":
            if hour == "12":
                hour == "00"
        else:
            hour = int(hour)+12
    

    time = f"{hour}:{minute}"

    ##Make sure that the time is the current time
    if minuteCheck != False:
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%M")
        if not minute == currentTime:
            raise Exception("ERROR: Time is not correct, minutes must match current")


    ##check in what timesones the time matches
    if minuteCheck != False:
        for timezone in pytz.common_timezones:
            timezonee = pytz.timezone(timezone)
            currentDateAndTime = datetime.now(timezonee)
            currentTime = currentDateAndTime.strftime("%H:%M")
            if time == currentTime:
                if timezone in zones:
                    break
        return timezone
    else:
        for timezone in pytz.common_timezones:
            timezonee = pytz.timezone(timezone)
            currentDateAndTime = datetime.now(timezonee)
            currentTime = currentDateAndTime.strftime("%H")
            if str(hour) == currentTime:
                if timezone in zones:
                    break
        return timezone

