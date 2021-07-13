from flask import Flask, render_template, request
import urllib.request, urllib.parse, urllib.error
import webbrowser
import mysql.connector
import json, re
import codecs
import http
import time
import ssl
import sys
import smtplib
import random
from geopy.geocoders import Nominatim

email=""
password=""
code = ""
db_password = #Database password
db_name = #Database for storing tables
email_name = #sender mail
email_password = #password of the email
app = Flask(__name__)

def where():
    global email,password
    if (email==""):
        return render_template('Home.html',login_alert="yes")
    conn = mysql.connector.connect(host = "localhost", user="root", passwd = db_password, database = db_name)
    cur = conn.cursor()
    cur.execute("SELECT home FROM accounts WHERE email='"+email+"';")
    work = cur.fetchone()
    work = work[0]
    cur.execute("SELECT location,id from works WHERE instr('"+work+"',domain)!=0;")
    fhand = codecs.open('static/js/where.js', 'w', "utf-8")
    fhand.write("myData = [\n")
    count = 0
    for row in cur :
        data = str(row[0]).split(", ")
        id = str(row[1])
        # print(data)
        lat = data[0]
        lng = data[1]
        if lat == 0 or lng == 0 : continue
        try :
            count+=1
            if count > 1 : fhand.write(",\n")
            output = "["+str(lat)+","+str(lng)+",'"+id+"']"
            fhand.write(output)
        except:
            continue
    fhand.write("\n];\n")
    cur.close()
    fhand.close()
    print(count, "records written to where.js")

@app.route('/work_info/',methods=["POST"])
def work_info():
    name = request.form["name"]
    deadline = request.form["deadline_date"]
    location = request.form["location"]
    email1 = request.form["email"]
    phone = request.form["phone"]
    aadhar = request.form["Aadhar Number"]
    domain = request.form["work_domain"]
    work_desc = request.form["work_desc"]
    if (location == "Current Location"):
        location = request.form["current_location"]
    else:
        location = request.form["location1"]
        api = 42
        url = 'http://py4e-data.dr-chuck.net/json?'
        address = location
        para = dict()
        para['address'] = address
        para['key'] = api
        url = url + urllib.parse.urlencode(para)
        uh = urllib.request.urlopen(url)
        data = uh.read()
        js = json.loads(data)
        lat = js['results'][0]['geometry']['location']['lat']
        lng = js['results'][0]['geometry']['location']['lng']
        location = str(lat) +", "+str(lng)
        # print((location.latitude, location.longitude))
    print(name,"\n",deadline,"\n",location,"\n",email1,"\n",phone,"\n",aadhar,"\n",domain,"\n",work_desc)
    try:
        conn = mysql.connector.connect(host = "localhost", user="root", passwd = db_password, database = db_name)
        cur = conn.cursor()
        cur.execute("INSERT INTO works(name, deadline, location, email, phone, aadhar, domain, descrip) VALUES('"+name+"','"+deadline+"','"+location+"','"+email1+"','"+phone+"','"+aadhar+"','"+domain+"','"+work_desc+"');")
        conn.commit()
        global email
        if (email==""):
            return render_template('Home.html',success2=1)
        else:
            return render_template('Home_success.html',success2=1)
    except:
        return render_template('Home.html',alert4="alert")

@app.route('/where/')
def where1():
    return render_template('where.html')

@app.route('/get_details/',methods=["POST"])
def get_details():
    global email
    id = request.form["id"]
    conn = mysql.connector.connect(host = "localhost", user="root", passwd = db_password, database = db_name)
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM works WHERE id='"+id+"';")
        work = cur.fetchone()
        id, name, deadline, location, email1, phone, aadhar, domain, descrip = work
        loc = location.split(", ")
        lat = loc[0]
        lng = loc[1]
        s = lat.split(".")
        s1=""
        x = float("0."+s[1])
        x1 = x*60
        x2 = int(x1)
        x3 = str(x1).split(".")
        x4 = float("0."+x3[1])
        x5 = x4*60
        x6 = s[0]+"+"+str(x2)+"+"+str(x5)+'+N'
        s = lng.split(".")
        s1=""
        x = float("0."+s[1])
        x1 = x*60
        x2 = int(x1)
        x3 = str(x1).split(".")
        x4 = float("0."+x3[1])
        x5 = x4*60
        x7 = s[0]+"+"+str(x2)+"+"+str(x5)+'+E'
        map_link = "https://www.google.com/maps/place/"+x6+"+"+x7
        print("https://www.google.com/maps/place/"+x6+"+"+x7)
        sender_email = email_name
        rec_email = email
        password = email_password
        message = "Greetings from Emplonnet, Here are the details of the work you requested for.\n\nid - "+str(id)+"\nname - "+str(name)+"\nDeadline Date - "+str(deadline)+"\nlocation - "+str(location)+"\nLocation in Google Map - "+map_link+"\nemail - "+str(email1)+"\nphone - "+str(phone)+"\naadhar - "+str(aadhar)+"\ndomain - "+str(domain)+"\ndescriptions about work - "+str(descrip)
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, rec_email, message)
            return render_template('where.html',alert1="The details have been sent to your mail. Please check your mail for the details of the work and contact the employer to avail it.")
        except:
            return render_template('where.html',alert2="Something went wrong. Please try again later")
    except:
        return render_template('where.html',alert2="Something went wrong. Please try again later")

@app.route('/remove_work/',methods=["POST"])
def remove_work():
    id = request.form['id']
    email1 = request.form["email"]
    conn = mysql.connector.connect(host = "localhost", user="root", passwd = db_password, database = db_name)
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM works WHERE id="+id+" AND email='"+email1+"';")
        conn.commit()
        where()
        return render_template('where.html',alert3="The Work you referred has been marked as Done.")
    except:
        return render_template('where.html',alert2="Something went wrong. Please try again later")


@app.route('/')
def index():
    return render_template('Home.html')

@app.route('/home/')
def home():
    global email,password
    if (email==""):
        return render_template('Home.html')
    else:
        return render_template('Home_success.html')

@app.route('/employee/')
def employee():
    return render_template('employee.html')

@app.route('/employee/',methods=["POST"])
def input():
    name=request.form["name"]
    print(name)
    return render_template('employee.html')

@app.route('/reset_pass/',methods=["POST"])
def reset_pass():
    global code, email
    sender_email = email_name
    rec_email = request.form["email"]
    email = rec_email
    password = email_password
    code = random.randint(100000,999999)
    message = "You have requested to reset password. The code for password reset is "+str(code)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        print(email,message)
        server.sendmail(sender_email, rec_email, message)
        return render_template('home_forgot.html',code_check="1")
    except:
        return render_template('Home.html',alert4="alert")

@app.route('/check_reset/',methods=["POST"])
def check_reset():
     if (str(code)==request.form["code"]):
         return render_template('home_forgot.html',correct=True)
     else:
        return render_template('home_forgot.html',code_check="1",alert5="alert")

@app.route('/confirm_reset/',methods=["POST"])
def confirm_reset():
    global email, password
    password = request.form["psw"]
    try:
        mydb = mysql.connector.connect(host = "localhost", user="root", passwd = db_password, database = db_name)
        mycursor = mydb.cursor()
        str1 = "UPDATE accounts SET pswd='"+password+"' WHERE email='"+email+"';"
        mycursor.execute(str1)
        mydb.commit()
        mycursor.close()
        mydb.close()
        return render_template('Home_success.html',success1="success")
    except:
        mycursor.close()
        mydb.close()
        return render_template('Home.html',alert4="alert")


@app.route('/aboutus/')
def aboutus():
    return render_template('about_us.html')

@app.route('/sign_up/',methods=["POST"])
def sign_up():
    name1 = request.form["name"]
    date = request.form["Date Of Birth"]
    gender = request.form["gender"]
    email1 = request.form["email"]
    phone = request.form["phone"]
    aadhar = request.form["Aadhar Number"]
    password1 = request.form["password"]
    home = ", ".join(request.form.getlist("works"))
    mydb = mysql.connector.connect(host = "localhost", user="root", passwd = db_password, database = db_name)
    mycursor = mydb.cursor()
    try:
        mycursor.execute("INSERT INTO accounts VALUES('"+name1+"','"+date+"','"+gender+"','"+email1+"','"+phone+"','"+aadhar+"','"+password1+"','"+home+"');")
        mydb.commit()
        mycursor.close()
        mydb.close()
        return render_template('Home_success.html',alert2="alert")
    except:
        mycursor.close()
        mydb.close()
        return render_template('Home.html',alert1="alert")

@app.route('/login/',methods=["POST"])
def login():
    global email,password
    email1 = request.form["email"]
    password1 = request.form["psw"]
    print(email,password)
    mydb = mysql.connector.connect(host = "localhost", user="root", passwd = db_password, database = db_name)
    mycursor = mydb.cursor()
    mycursor.execute("SELECT email,pswd FROM accounts WHERE email='"+email1+"'")
    creden = mycursor.fetchone()
    print(creden)
    try:
        if (password1==creden[1]):
            email=email1
            password=password
            return render_template('Home_success.html',alert3="alert")
        else:
            return render_template('Home.html',alert2="alert")
    except:
        return render_template('Home.html',alert2="alert")
#webbrowser.get().open("http://localhost:5000")

@app.route('/google_map/',methods=["POST"])
def google_map():
    id = request.form['id']
    mydb = mysql.connector.connect(host = "localhost", user="root", passwd = db_password, database = db_name)
    mycursor = mydb.cursor()
    try:
        mycursor.execute("SELECT location FROM works WHERE id='"+id+"';")
        pos = mycursor.fetchone()
        pos = str(pos[0]).split(", ")
        lat = pos[0]
        lng = pos[1]
        print(lat,lng)
        s = lat.split(".")
        s1=""
        x = float("0."+s[1])
        x1 = x*60
        x2 = int(x1)
        x3 = str(x1).split(".")
        x4 = float("0."+x3[1])
        x5 = x4*60
        x6 = s[0]+"\u00B0"+str(x2)+"'"+str(x5)+'"N'
        s = lng.split(".")
        s1=""
        x = float("0."+s[1])
        x1 = x*60
        x2 = int(x1)
        x3 = str(x1).split(".")
        x4 = float("0."+x3[1])
        x5 = x4*60
        x7 = s[0]+"\u00B0"+str(x2)+"'"+str(x5)+'"E'
        webbrowser.get().open("https://www.google.com/maps/place/"+x6+"+"+x7)
        print("https://www.google.com/maps/place/"+x6+"+"+x7)
        return render_template('where.html')
    except:
        return render_template('where.html',alert2="error")

@app.route('/logout/')
def logout():
    global email,password
    email=""
    password=""
    return render_template('Home.html')

@app.route('/work/')
def work():
    return render_template('do_work.html')
webbrowser.get().open("http://localhost:5000/")

if __name__ == '__main__':
  app.run(debug=False)
