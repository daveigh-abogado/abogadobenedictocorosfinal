import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")

services_db = myclient["services"]
users_db = myclient["users"]
appts_db = myclient["appts"]
slots_db = myclient["slots"]

def create_appt(appt):
    appts_coll = appts_db['appts']
    appts_coll.insert_one(appt)

def get_appts(user):
    appointments = []
    appts_coll = appts_db['appts']
    if user == 'admin':
        for a in appts_coll.find({}):
            appointments.append(a)
    else:
        for a in appts_coll.find({"username":user}):
            appointments.append(a)
    return appointments
    


def testing(day, time):
    timeslots_coll = slots_db["slots"]
    day_to_flip = get_day(day)

    rooms = ['Room1', 'Room2', 'Room3']
    for a in rooms:
        room = day_to_flip[a]
        if room[time]==0:
            room[time]=1
            break
    return room

def get_day(day):
    timeslots_coll = slots_db["slots"]
    return timeslots_coll.find_one({"code":day})

def get_timeslots(day, service_time):
    timeslots_coll = slots_db["slots"]
    backend_available_slots = []
    available_slots = []

    test = timeslots_coll.find_one({"code":day})
    rooms = ['Room1', 'Room2', 'Room3']
    for a in rooms:
        room = test[a]
        i = 0
        for x in room:
            if x==0:
                if room[i+(service_time-1)] == 0:
                    backend_available_slots.append([room, i])
                    available_slots.append(i)
            i+=1
            if i==10-service_time:
                break
    return available_slots

def reservetime(time, day, service):
    timeslots_coll = slots_db["slots"]
    day_to_flip = get_day(day)

    rooms = ['Room1', 'Room2', 'Room3']
    for a in rooms:
        room = day_to_flip[a]
        if room[time]==0:
            b = 0
            while b < service:
                room[time+b]=1
                b+=1
            timeslots_coll.update_one({"code":day}, {"$set":{a:room}})
            break
    return day
    
def resetslots():
    week = []
    timeslots_coll = slots_db["slots"]
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    for d in days:
        week.append(get_day(d))

    rooms = ['Room1', 'Room2', 'Room3']
    for day in week:
        for room in rooms:
            timeslots_coll.update_one({"code":day["code"]}, {"$set":{room:[0,0,0,1,0,0,0,0,0]}})
    return 'Slots were reset for the week.'

def get_users():
    user_list = []
    users_coll = users_db['users']
    for u in users_coll.find({}):
        user_list.append(u)

    return user_list

def get_user(username):
    users_coll = users_db['users']
    user=users_coll.find_one({"username":username})
    return user

def get_service(code):
    services_coll = services_db["services"]
    service = services_coll.find_one({"code":code},{"_id":0})

    return service

def get_services():
    services = []

    services_coll = services_db["services"]

    for s in services_coll.find({},{"_id":0}):
        services.append(s)

    return services


