from FlyOlinFly import app
from FlyOlinFly.models import Entry
from FlyOlinFly.database import init_db, db_session
from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash 
from datetime import datetime
import requests

@app.route('/')
def auth():
	return redirect('http://olinapps.com/external?callback=http://127.0.0.1:5000/authed')

#Authentication - Inspried by TCR from OlinAppsDirectory

def load_session(sessionid):
	r = requests.get('http://olinapps.com/api/me?sessionid=' + sessionid)
	if r.status_code == 200:
			session['sessionid'] = sessionid
			session['userdata'] = r.json()
			session['logged_in'] = True
			session['tracker'] = 0
			return True
	return False


@app.route('/authed', methods=['POST','GET'])
def landing():
	if request.method == "POST":
		if request.form.has_key('sessionid') and load_session(request.form.get('sessionid')):
			return redirect(url_for('content'))
		else:
			session.pop('sessionid',None)
	session['logged_in'] = False
	return render_template('main.html', entries=None)

@app.route('/close', methods=['GET', 'POST'])
def logout():
	session.pop('sessionid', None)
	session.pop('user', None)
	return redirect('/')
	
def unique_list(sessionid):
	r2 = requests.get('http://directory.olinapps.com/api/people?sessionid=' + sessionid)
	if r2.status_code == 200:
		raw = r2.json()
		parsed = dict()
		for i in range(len(raw['people'])):
			parsed[raw['people'][i]['name']] = raw['people'][i]['id']
		session['idDB'] = parsed
		
		return True
		
@app.route('/content')
def content():
	tracker = session.get('tracker')
	userdata = session.get('userdata')
	user = userdata['user']
	name = user['id'].split('.')
	if tracker == 0:
		###For future Olin Directory Integration
		#sessionid = session.get('sessionid')
		#unique_list(sessionid)
		#parsed = session.get('idDB')
		flash("Welcome to FlyOlinFly" + ", " + name[0].title())
	cur = db_session.execute('select fname, lname, phonenum, email, flightdesc, datetime from entry order by datetime')
	entries = [dict(fname=row[0], lname=row[1], phonenum=row[2], email=row[3], flightdesc=row[4], date=datetime.strftime(row[5], "%m/%d/%Y"), time=datetime.strftime(row[5], "%I:%M %p")) for row in cur.fetchall()]
	username = name[0].title() + name[1].title()
	return render_template('main.html', entries=entries, user=username)
	
@app.route('/add', methods=['POST'])
def add_newentry():
	if not session.get('logged_in'):
			abort(401)
	else:
		fname = request.form['fname']
		lname = request.form['lname']
		phonenum = request.form['phonenum']
		email = request.form['email']
		flightdesc = request.form['flightdesc']
		date = request.form['date']
		time = request.form['time']
		
		
		###THIS IS TEMPORARY
		unique = request.form['email'].split('@')[0]
			
		userdata = session.get('userdata')
		user = userdata['user']
		
		###ACTUAL UNIQUE SET IS HERE
		#unique = user['id']
		
		###This is to grab the OlinDirectory ID 
		###The following code is for use in a later version	
		#name = user['id'].split('.')
		#username = name[0].title() + " " + name[1].title()
		#parsed = session.get('idDB')
		
		
		###parse the date and time data to fit a python datetime object###
	
		datetime1 = datetime.strptime(date + " " + time, "%m/%d/%Y %I:%M %p")
		
		###WARNING: USERS MUST NOT ADD ENTRIES FOR ANYONE BUT THEMSELVES
		#this is not an ideal solution, and when I can get PUT access
		#things can be fixed. Until then - 
		
		#checkexist = Entry.query.filter_by(unique=user['id']).first()
		checkexist = None
		
		if checkexist == None:
			newentry= Entry(fname, lname, phonenum, email, flightdesc, datetime1, unique)
			db_session.add(newentry)
			flash('You have added an entry')
			flash(unique)
		else:
			checkexist.fname = fname
			checkexist.lname = lname
			checkexist.phonenum = phonenum
			checkexist.email = email
			checkexist.flightdesc = flightdesc
			checkexist.datetime = datetime1
			flash('You have modified your entry')
		
		db_session.commit()
		
		session['tracker'] += 1
		
		return redirect(url_for('content'))
