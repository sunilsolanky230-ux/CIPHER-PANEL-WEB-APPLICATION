from flask import Flask, render_template, request, redirect, session
import sqlite3
import bcrypt
import random
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = "cyber_project_secret"

# encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

# security logs
logs = []

def get_db():
    return sqlite3.connect("database.db")


@app.route("/")
def home():
    return redirect("/login")


# REGISTER
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (username,hashed)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():

    error=None

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        conn=get_db()
        cur=conn.cursor()

        cur.execute(
        "SELECT password FROM users WHERE username=?",
        (username,)
        )

        user=cur.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode(),user[0]):

            otp=str(random.randint(100000,999999))

            session["otp"]=otp
            session["temp_user"]=username

            logs.append("Login successful")

            print("OTP:",otp)

            return redirect("/otp")

        else:

            error="Invalid username or password"
            logs.append("Failed login attempt")

    return render_template("login.html",error=error)


# OTP
@app.route("/otp",methods=["GET","POST"])
def otp():

    error=None

    if "otp" not in session:
        return redirect("/login")

    if request.method=="POST":

        entered=request.form["otp"]

        if entered==session["otp"]:

            session["user"]=session["temp_user"]

            session.pop("otp")
            session.pop("temp_user")

            logs.append("OTP verified")

            return redirect("/dashboard")

        else:

            error="Invalid OTP"
            logs.append("OTP verification failed")

    return render_template("otp.html",error=error)


# DASHBOARD
@app.route("/dashboard",methods=["GET","POST"])
def dashboard():

    if "user" not in session:
        return redirect("/login")

    encrypted=None
    decrypted=None
    error=None

    if request.method=="POST":

        text=request.form["message"].strip()
        action=request.form["action"]

        if text=="":

            error="Please enter text"

        else:

            if action=="encrypt":

                encrypted=cipher.encrypt(text.encode()).decode()
                logs.append("Encryption executed")

            elif action=="decrypt":

                try:

                    decrypted=cipher.decrypt(text.encode()).decode()
                    logs.append("Decryption executed")

                except:

                    error="Invalid ciphertext"
                    logs.append("Invalid ciphertext attempt")

    return render_template(
    "dashboard.html",
    user=session["user"],
    encrypted=encrypted,
    decrypted=decrypted,
    error=error,
    logs=logs
    )


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()
    logs.append("User logged out")

    return redirect("/login")


if __name__=="__main__":
    app.run(debug=True)