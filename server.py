from flask import Flask, render_template, redirect, request, flash, session
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re
app = Flask(__name__)
app.secret_key = "NotYours"
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/checkReg", methods=["POST"])
def checkReg():
 
    if ("_flashes" in session.keys()):
        session["firstName"] = request.form["firstName"]
        session["lastName"] = request.form["lastName"]
        session["email"] = request.form["email"]
        return redirect("/")    
    
    if (len(request.form['firstName']) == 0):
        flash("First Name field cannot be left blank", "firstName")
    elif (len(request.form['firstName']) <= 2):
        flash("First Name must have 2+ characters", "firstName")
        print("**********************************************")
    elif not(NAME_REGEX.match(request.form["firstName"])):
        flash("First Name format invalid", "firstName")

    if (len(request.form['lastName']) == 0):
        flash("Last Name field cannot be left blank", "lastName")
    elif (len(request.form['lastName']) <= 2):
        flash("Last Name must have 2+ characters", "lastName")
    elif not(NAME_REGEX.match(request.form["lastName"])):
        flash("Last Name format invalid ", "lastName")

    query = "SELECT * FROM users WHERE email=%(email)s;"
    data= {
        "email": request.form["email"]
    }
    mysql = connectToMySQL("loginReg")
    result = mysql.query_db(query,data)
    
    if (len(request.form['email']) == 0):
        flash("Email field cannot be left blank", "email")
    if not (EMAIL_REGEX.match(request.form['email'])):
        flash("Emai format invalid", "email")
    if (result):
        flash("Email address entered is already registered", "email")
        return redirect ("/")

    if (len(request.form["password"]) == 0):
        flash("Password field cannot be left blank","password")
    if (len(request.form["password"]) <= 8):
        flash("Password field must be 8+ characters","password")
    if (len(request.form["confirmPassword"]) < 1 or (request.form['confirmPassword'] != request.form["password"])):
        flash("Passwords entered do not match")
        return redirect("/")
    else:
        pw_hash = bcrypt.generate_password_hash(request.form["password"])
        sqlInsert = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(firstName)s, %(lastName)s, %(email)s, %(password_hash)s);"
        data= {
            "firstName": request.form["firstName"],
            "lastName": request.form["lastName"],
            "email": request.form["email"],
            "password_hash": pw_hash
        }
        mysql = connectToMySQL("loginReg")
        result = mysql.query_db(sqlInsert, data)
        session["firstName"] = request.form["firstName"]
        flash("You've been successfully registered", "success")
        return redirect("/success")

@app.route("/success")
def success():
    if ("firstName" in session):
        return render_template("success.html", name = session["firstName"])
    else:
        session.clear()
        flash("You must be logged in to enter this website", "logout")
        return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out", "logout")
    return redirect("/")

@app.route("/checkLog", methods=["POST"])
def check_login():
    login_query = "SELECT * FROM users WHERE email=%(email)s"
    data={
        "email": request.form["email"]
    }
    mysql = connectToMySQL("loginReg")
    result = mysql.query_db(login_query, data)
    if (result):
        if bcrypt.check_password_hash(result[0]["password"], request.form["password"]):
            session["firstName"] = result[0]["first_name"]
            return redirect("/success")
        else:
            flash("Incorrect credentials", "reg")
            return redirect("/")
    else:
        return redirect("/")
    return render_template("/success.html")
    

if (__name__ == "__main__"):
    app.run(debug=True)
