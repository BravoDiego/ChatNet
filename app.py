from flask import Flask, flash, redirect, render_template, url_for, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

from helpers import apology, login_required
import sqlite3

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

con = sqlite3.connect("messages.db", check_same_thread=False)
db = con.cursor()

def get_user():
    return db.execute("SELECT username FROM users WHERE id = ?", [session["user_id"]]).fetchone()[0]

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("logout")
    return redirect("/")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def chat():
    if request.method == "GET":
        infos = db.execute("""SELECT username, timemessages, messages FROM sentmessages 
                            JOIN users ON sentmessages.user_id = users.id 
                            """).fetchall()
        username = get_user()
        messages = [
            {
                "message": ele[2],
                "username": ele[0],
                "time": ele[1][:-3],
                "usertest": ele[0] == username
            }
            for ele in infos
        ]
        #print(messages)
        return render_template("chat.html", messages=messages)
    else: 
        db.execute("INSERT INTO sentmessages (user_id, messages) VALUES (?, ?)", [session["user_id"], request.form.get("message")])
        con.commit()  
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "GET":
        return render_template("login.html")

    else:
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        #print(request.form.get("username"))
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", [request.form.get("username")]
        ).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0][2], request.form.get("password")
        ):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        flash("You've been logged in", category="info")
        return redirect("/#footerchat")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("/register.html")
    else:
        # User's prompt
        name = request.form.get("username")
        password = request.form.get("password")
        confirm_pwd = request.form.get("confirmation")

        username_in_db = db.execute("SELECT * FROM users").fetchall()

        if not name or not password or not confirm_pwd or not (password == confirm_pwd):
            return apology("An error has occurred")
        else:
            for ele in username_in_db:
                if ele[1] == name:
                    return apology("Please choose another username")
                
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", [name, generate_password_hash(password)])
            con.commit()

            flash("You were well registered")
            return redirect("/")
        
@app.route("/history", methods=["GET", "POST"])
def history():
    if not session["user_id"]:
        return apology("Please log in before view history")
    
    infos = db.execute("""SELECT username, timemessages, messages FROM sentmessages 
                            JOIN users ON sentmessages.user_id = users.id 
                            WHERE user_id = ?
                            """, [session["user_id"]]).fetchall()
    #print(infos)
    mes_history = [
            {
                "message": ele[2],
                "username": ele[0],
                "time": ele[1][:-3],
            }
            for ele in infos
        ]
    return render_template("history.html", messages=mes_history)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "GET":
        return render_template("account.html", username=get_user())
    else:
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
        
        elif not request.form.get("new_password"):
            return apology("must provide new_password")
        
        hash_account = db.execute("SELECT hash FROM users WHERE id = ?", [session["user_id"]]).fetchone()[0]
        if not check_password_hash(hash_account, request.form.get("password")):
            return apology("password must be your current password")
        
        usernames = db.execute("SELECT username FROM users").fetchall()
        for e in usernames:
            if e[0] == request.form.get("new_password"):
                return apology("Please choose an another username")
        
        db.execute("""UPDATE users SET username = ?, hash = ? WHERE id = ?""", [request.form.get("username"), generate_password_hash(request.form.get("new_password")), session["user_id"]])
        con.commit()

        flash("You've changed your information")
        return redirect("/account")

@app.route("/delete", methods=["GET"])
def delete():
    if request.method == "GET":
        db.execute("""UPDATE sentmessages SET user_id = 1 WHERE user_id = ?""", [session["user_id"]])
        con.commit()
        db.execute("DELETE FROM users WHERE id = ?", [session["user_id"]])
        con.commit()
        flash("You've deleted your account")
        return redirect("/logout")


if __name__=="__main__":
    app.run(host='localhost', port=5000)