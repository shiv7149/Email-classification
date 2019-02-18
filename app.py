from flask import Flask,render_template,redirect,request,url_for,session,jsonify,flash
from flask_mysqldb import MySQL,MySQLdb
from flask_uploads import UploadSet , configure_uploads, IMAGES
from flask_mail import Mail, Message
import smtplib


app = Flask(__name__)
app.secret_key = "secretkey"

#uploading pics
photos = UploadSet('photo',IMAGES)
app.config['UPLOADED_PHOTO_DEST'] = 'static/uploads'
configure_uploads(app, photos)

#mail config
app.config.update(
	DEBUG = True,
	MAIL_SERVER = 'smtp.gmail.com',
	MAIL_PORT = 465,
	MAIL_USE_SSL = True,
	MAIL_USERNAME = 'vcharm.demo@gmail.com',
	MAIL_PASSWORD = 'Har7209pal'
	)
s_mail = Mail(app)

#SQL Connectivity
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='flaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)

#home
@app.route('/')
def home():
	cur = mysql.connection.cursor()
	cur.execute("SELECT name FROM doctors")
	data = cur.fetchall()
	cur.close()
	return render_template('index.html', data=data)
    

#sending mail
@app.route('/sent form')
def mail():
	return render_template("mail.html")

@app.route("/send-mail",methods=["GET","POST"])
def send_mail():
	if request.method == 'GET':
		return "Get method"
	else:
		email_add = request.form['Email_Address']
		sub = request.form['Subject']
		mess = request.form['Message']
		try:
			msg = Message(sub, sender = "vcharm.demo@gmail.com", recipients = [email_add])
			msg.body = mess
			s_mail.send(msg)
			return "Sent"
		
		except Exception as e:
			return str(e)

#forget password
@app.route('/forget-password/')
def forget_password():
    return render_template("forget.html")


@app.route('/just-send-password',methods=["GET","POST"])
def made_max():
	if request.method == "POST":
		email = request.form['email']
		
		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("SELECT * fROM users WHERE email = %s",(email,))
		user = cur.fetchone()
		cur.close()
		
		if len(user) > 0:
			#if bcrypt.check_password_hash(user['password'], password):
			if (email == user['email']):
				name = user['name']
				password = user['password']
				mess = "Hello \t"+name+"\n below is your password\n"+password
				try:
					msg = Message("Forget password", sender = "vcharm.demo@gmail.com", recipients = [email])
					msg.body = mess
					s_mail.send(msg)
					return "Sent"
		
				except Exception as e:
					return str(e)
				
			else:
				return "mail Do not match"
		else:
			return "Enter mail "
	else:
		return render_template("login.html")
    

#admin
@app.route('/admin/')
def admin():
    return render_template("login.html")

@app.route('/admin/home')
def admin_home():
    return render_template("admin.html")
	
@app.route('/admin/register', methods=["GET","POST"])
def register():

	if request.method == 'GET':
		return render_template("login.html")
	else:
		name = request.form['name']
		password = request.form['password'].encode('utf-8')
		email = request.form['email']
		role = request.form['user_role']
		if 'photo' in request.files:
			file = photos.save(request.files['photo'])

		filename = "uploads/"+file


		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO users (name,password,role,filename,email) VALUES (%s,%s,%s,%s,%s)",(name,password,role,filename,email)) #hash_password
		mysql.connection.commit()
		session['name'] = name
		session['path'] = filename
		return render_template("admin.html")
		
@app.route('/admin/login', methods=["GET","POST"])
def login():
	if request.method == "POST":
		name = request.form['name']
		password = request.form['password'].encode('utf-8')
		role = request.form['user_role']
		
		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("SELECT * fROM users WHERE name = %s",(name,))
		user = cur.fetchone()
		cur.close()
		
		if len(user) > 0:
			#if bcrypt.check_password_hash(user['password'], password):
			if (password == user['password'].encode('utf-8') and role == user['role']):
				session['name'] = name
				session['path'] = user['filename']
				return render_template("admin.html")
			else:
				return "password is wrong"
		else:
			return "Enter Username "
	else:
		return render_template("login.html")


@app.route('/message', methods=["GET","POST"])
def message():
	if request.method == 'GET':
		return render_template("index.html")
	else:
		name = request.form['name']
		email = request.form['email']
		phone = request.form['phone']
		enquiry = request.form['enquiry']
		
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO enquiry (name,email,phone,enquiry) VALUES (%s,%s,%s,%s)",(name,email,phone,enquiry))
		mysql.connection.commit()
		return "your enquiry is:\t" +enquiry+"."

@app.route('/user')
def user():
	return render_template("user.html")
 
@app.route('/logout')
def logout():
	session.clear()
	return render_template("admin.html")



#Doctor tab
@app.route('/add')
def add():
	return render_template("add doctor.html")


@app.route('/doc_add',methods=["GET","POST"])
def doc_add():
	if request.method == 'GET':
		return "false"
	else:
		name = request.form['name']
		email = request.form['email']
		mobile = request.form['mobile']
		department = request.form['department']
		address = request.form['address']
		specialist = request.form['specialist']

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO doctors (name,email,mobile,department,address,specialist) VALUES (%s,%s,%s,%s,%s,%s)",(name,email,mobile,department,address,specialist))
		mysql.connection.commit()
		return render_template('add doctor.html')
		

@app.route('/doctor list')
def doc_list():
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM doctors")
	data = cur.fetchall()
	return render_template('doctor list.html', data=data)


#Department tab
@app.route('/add-department')
def add_department():
	return render_template("add department.html")


@app.route('/adding',methods=["GET","POST"])
def adding():
	if request.method == 'GET':
		return "false"
	else:
		department = request.form['department']
		description = request.form['description']
		

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO departments (department,description) VALUES (%s,%s)",(department,description))
		mysql.connection.commit()
		return render_template('add department.html')
		

@app.route('/department list')
def dep_list():
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM departments")
	data = cur.fetchall()
	return render_template('department list.html', data=data)


#Paitent tab
@app.route('/add-patient')
def add_patient():
	return render_template("add patient.html")


@app.route('/patient',methods=["GET","POST"])
def patient():
	if request.method == 'GET':
		return "false"
	else:
		name = request.form['name']
		email = request.form['email']
		password = request.form['password']
		mobile = request.form['mobile']
		blood_group = request.form['blood_group']
		sex = request.form['sex']
		date_of_birth = request.form['date_of_birth']
		address = request.form['address']
		

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO patient (name,email,password,mobile,blood_group,sex,date_of_birth,address) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(name,email,password,mobile,blood_group,sex,date_of_birth,address))
		mysql.connection.commit()
		cur = mysql.connection.cursor()
		cur.execute("SELECT name FROM doctors")
		data = cur.fetchall()
		cur.close()
		flash("Registeration successfull! ")
		return render_template('index.html', data=data)
		
		
		

@app.route('/patient list')
def pat_list():
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM patient")
	data = cur.fetchall()
	return render_template('patient list.html', data=data)

#Appointment tab
@app.route('/add-appointment')
def add_appointment():
	cur = mysql.connection.cursor()
	cur.execute("SELECT name FROM doctors")
	data = cur.fetchall()
	cur.close()
	return render_template('add appointment.html', data=data)
	


@app.route('/appointment',methods=["GET","POST"])
def appointment():
	if request.method == 'GET':
		return "false"
	else:
		name = request.form['name']
		department = request.form['department']
		doctor = request.form['doctor']
		date_ = request.form['date_']
		problem = request.form['problem']
		

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO appointment (name,department,doctor,date_,problem) VALUES (%s,%s,%s,%s,%s)",(name,department,doctor,date_,problem))
		mysql.connection.commit()
		return "appointment added successfully"
		

@app.route('/appointment list')
def app_list():
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM appointment")
	data = cur.fetchall()
	return render_template('appointment list.html', data=data)





			

if __name__ == "__main__":
	app.run( debug = True )
