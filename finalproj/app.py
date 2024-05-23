from flask import Flask,redirect
from flask import render_template, request, session, flash
import database as db
import apptmanagement as am
import authentication
import logging

app = Flask(__name__)

app.secret_key = 'dental'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/services')
def services():
    service_list = db.get_services()
    return render_template('services.html', page="Services", services=service_list)

@app.route('/servicedetails')
def servicedetails():
    code = request.args.get('code', '')
    service = db.get_service(int(code))

    return render_template('servicedetails.html', code=code, service=service)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods = ['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    fmessage = 'Invalid username or password. Please try again.'

    if username=='' or password=='':
        flash(fmessage)
        return redirect('/login')
    
    test = db.get_user(username)
    if test is None:
        flash(fmessage)
        return redirect('/login')
    
    if test["password"] != password:
        flash(fmessage)
        return redirect('/login')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.pop("user",None)
    return redirect('/')

@app.route('/makeappt')
def makeappt():
    services = db.get_services()
    return render_template('appointment.html', services=services)

@app.route('/checktimeslots', methods = ['POST'])
def checktimeslots():
    s = request.form.get('service')
    service = db.get_service(int(s))
    day = request.form.get('day')
    available_slots=db.get_timeslots(day, service["time"])

    available_slots.sort()
    
    actual_slots = []
    equivalent = ['8AM','9AM','10AM','11AM','12NN','1PM','2PM','3PM','4PM','5PM']
    for i in available_slots:
        if equivalent[i] in actual_slots:
            continue
        actual_slots.append(equivalent[i])

    return render_template('showappointment.html', actual_slots=actual_slots, day=day, service=service["time"])    

@app.route('/reserve', methods=['POST'])
def reserve():
    t = request.form.get('time')
    service = request.form.get('service')
    equivalent = ['8AM','9AM','10AM','11AM','12NN','1PM','2PM','3PM','4PM','5PM']
    j = 0
    for i in equivalent:
        if t == i:
            time = j
            break
        j+=1
    day = request.args.get('day', '')
    display_day = db.reservetime(time, day, int(service))
    a = db.get_day(display_day)

    am.create_appt_from_session(day, t)
    return render_template('success.html', a=a)

@app.route('/editslots')
def editslots():
    return render_template('editslots.html')

@app.route('/resetslots')
def resetflots():
    message = db.resetslots()
    flash(message)
    return redirect('/editslots')

@app.route('/viewappointments')
def viewappointments():
    appointments = db.get_appts(session["user"]["username"])
    return render_template('viewappointments.html', page="Appointments", appointments=appointments)
