from FlyOlinFly import app
from FlyOlinFly.models import Entry
from FlyOlinFly.database import init_db, db_session
from sqlalchemy.exc import IntegrityError
from flask import Flask, request, session, g, redirect, url_for, \
	abort, render_template, flash 
from datetime import datetime
import requests, re

@app.route('/')
def auth():
	return redirect('http://www.olinapps.com/external?callback=http://0.0.0.0:5000/authed')

#Authentication - Inspried by TCR from OlinAppsDirectory

def load_session(sessionid):
	r = requests.get('http://www.olinapps.com/api/me?sessionid=' + sessionid)
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
	r2 = requests.get('http://wwww.olinapps.com/api/me?sessionid=' + sessionid)
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
	cur = db_session.execute('select fname, lname, phonenum, email, flightdesc, datetime, comment, sorter from entry order by datetime')
	giver_rows = []
	entries_rows = []

	for row in cur.fetchall():
		if row[7] == "offering":
			giver_rows.append(row)
			print(row[7])
		else:
			entries_rows.append(row)
			print(row[7])

	givers = [dict(fname=row[0], lname=row[1], phonenum=row[2],
				email=row[3], comment=row[6]) for row in giver_rows]

	entries = [dict(fname=row[0], lname=row[1], phonenum=row[2],
				email=row[3], flightdesc=row[4], date=datetime.strftime(row[5], "%m/%d/%Y"),
				time=datetime.strftime(row[5], "%I:%M %p"), comment=row[6]) for row in entries_rows]
	username = name[0].title() + name[1].title()
	return render_template('main.html', givers=givers, entries=entries, user=username)
	
@app.route('/add', methods=['POST'])
def add_newentry():
	if not session.get('logged_in'):
			abort(401)
	else:
		fname = request.form['fname']
		lname = request.form['lname']
		phonenum = ''.join(re.split('\D+', request.form['phonenum']))
		email = request.form['email']
		flightdesc = request.form['flightdesc']
		date = request.form['datepicker']
		time = request.form['timepicker']
		comment = request.form['comment']
		sorter = request.form['sorter']

		###WARNING: USERS MUST NOT ADD ENTRIES FOR ANYONE BUT THEMSELVES
		#this is not an ideal solution, and when I can get PUT access
		#things can be fixed. Until then - 
		
		###UNIQUE IS SET HERE
		userdata = session.get('userdata')
		user = userdata['user']
		unique = user['id']
		
		###This is to grab the OlinDirectory ID 
		###The following code is for use in a later version	
		#name = user['id'].split('.')
		#username = name[0].title() + " " + name[1].title()
		#parsed = session.get('idDB')

		session['tracker'] += 1
		
		#quick and dirty form validation
		namecheck = 0
		phonecheck = 0
		emailcheck = 0
		flightcheck = 0
		datetimecheck = 0
		commentcheck = 0
		
		if len(fname) != 0 and len(lname) != 0:
			namecheck = 1
		if len(phonenum) == 10:
			phonecheck = 1
		if email:
			emailcheck = 1
		if flightdesc:
			flightcheck = 1
		###parse the date and time data to fit a python datetime object###
		try:
			datetime1 = datetime.strptime(date + " " + time, "%m/%d/%Y %I:%M %p")
			datetimecheck = 1
		except:
			datetimecheck = 0

		if len(comment) > 140:
			commentcheck = 1

		sum = namecheck + phonecheck + emailcheck + flightcheck + datetimecheck
		if sum == 5:
			session['valid'] = True
			checkexist = Entry.query.filter_by(unique=user['id']).first()
			#checkexist = None
			if checkexist == None:
				try:
					newentry= Entry(fname, lname, phonenum, email, flightdesc, datetime1, unique, comment, sorter)
					db_session.add(newentry)
					db_session.commit()		
					flash('You have added an entry')
				except IntegrityError, e:
					key = e.message.split('key')[1].split("'")[1]
					translate = {'phonenum': 'phone number', 'email': 'e-mail'}
					flash('Someone has the same ' + translate[key] + ' as you. Please contact an administrator.')
			else:
				checkexist.fname = fname
				checkexist.lname = lname
				checkexist.phonenum = phonenum
				checkexist.email = email
				checkexist.flightdesc = flightdesc
				checkexist.datetime = datetime1
				checkexist.comment = comment
				checkexist.sorter = sorter
				db_session.add(checkexist)
				db_session.commit()	
				flash('You have modified your entry')
		
		
			return redirect(url_for('content'))
			
		else:
			session['valid'] = False
			fix = list()
			fixthis = str()
			
			if namecheck == 0:
				fix.append("name")
			if phonecheck == 0:
				fix.append("phone number")
			if emailcheck == 0:
				fix.append("email")
			if flightcheck == 0:
				fix.append("flight description")
			if datetimecheck == 0:
				fix.append("arrival date and time")
			if commentcheck == 0:
				fix.append("comment")
			
			if len(fix) > 2:
				last = fix[-1]
				for i in fix:
					if i == last:
						fixthis = fixthis + " and " + i
					else:
						fixthis = fixthis + " " + i + ","
				flash('Your form has failed to validate. Please check that your ' + fixthis + ' are all correct.')
			elif len(fix) == 2:
				fixthis = fix[0] + " and " + fix[1]
				flash('Your form has failed to validate. Please check that your ' + fixthis + ' are both correct.')
			elif len(fix) == 1:
				fixthis = fix[0]
				flash('Your form has failed to validate. Please check that your ' + fixthis + ' is correct.')
				flash(phonenum)
			return redirect(url_for('content'))
