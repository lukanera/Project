from flask import Flask, render_template, url_for, redirect, request, session, flash
import sqlite3
import os
from init_db import init_db, init_db2

app = Flask(__name__)
DATABASE = "database.db"
DATABASE2 = "database2.db"
app.secret_key = "i am so secret that i must increase rent for poor people."


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def register(self):
        try:
            conn = sqlite3.connect(DATABASE, timeout=20)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (self.username, self.password))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def login(self):
        conn = sqlite3.connect(DATABASE, timeout=20)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (self.username,))
        record = cursor.fetchone()
        conn.close()
        if record and record[0] == self.password:
            return True
        return False


class Game:
    def __init__(self, name, release_year, image_url):
        self.name = name
        self.release_year = release_year
        self.image_url = image_url

    def addgame(self):
        try:
            with sqlite3.connect(DATABASE2, timeout=10, check_same_thread=False) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO games (name, release_year, image_url) VALUES (?, ?, ?)',
                               (self.name, self.release_year, self.image_url))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False




@app.route('/')
def home():
    if 'username' in session:
        games = [
            {"rank": 1, "title": "Baldurs Gate 3", "year": 2023, "rating": 99, "image_url": "static/images/images.jpeg"},
            {"rank": 2, "title": "The Legend of Zelda: Ocarina of Time", "year": 1998, "rating": 99, "image_url": "static/images/download.jpeg"},
            {"rank": 3, "title": "Tony Hawk's Pro Skater 2", "year": 2000, "rating": 98, "image_url": "static/images/tony-hawk-prp-skater-2-1639763193495.jpg"},
            {"rank": 4, "title": "Grand Theft Auto IV", "year": 2008, "rating": 98, "image_url": "static/images/zfuvi63q63o41.png"},
            {"rank": 5, "title": "SoulCalibur", "year": 1999, "rating": 98, "image_url": "static/images/pFA9HCIBstlal2O1ZxGeHDa0G4QtmusC.jpeg"},
            {"rank": 6, "title": "Super Mario Galaxy", "year": 2007, "rating": 97, "image_url": "static/images/SuperMarioGalaxy.jpg"},
            {"rank": 7, "title": "Super Mario Galaxy 2", "year": 2010, "rating": 97, "image_url": "static/images/Super_Mario_Galaxy_2_Box_Art.jpg"},
            {"rank": 8, "title": "Red Dead Redemption 2", "year": 2018, "rating": 97, "image_url": "static/images/images (1).jpeg"},
            {"rank": 9, "title": "Grand Theft Auto V", "year": 2014, "rating": 97, "image_url": "static/images/gta-5-button-2021-1639777058682.jpg"},
            {"rank": 10, "title": "Disco Elysium: The Final Cut", "year": 2021, "rating": 97, "image_url": "static/images/MV5BY2UxMTY2OTUtMzBlMy00Zjk4LThmY2UtMzVhOTlkOWEwYjdkXkEyXkFqcGdeQXVyMTMxNDI1OTQx._V1_.jpg"},
            {"rank": 11, "title": "The Legend of Zelda: Breath of the Wild", "year": 2017, "rating": 97, "image_url": "static/images/111060.jpg"},
            {"rank": 12, "title": "Tony Hawk's Pro Skater 3", "year": 2001, "rating": 97, "image_url": "static/images/tony-hawk-pro-skater-3-button-crop-1643413502830.jpg"}
        ]
        flash(f'Logged in as {session["username"]}')
        return render_template("home.html", games=games)
    flash("You have to login to see homepage.")
    return redirect(url_for('login'))




@app.route("/register", methods = ['POST', 'GET'])
def register():
    if "username" in session:
        flash('you have to logout before you can register again')
        return render_template('home.html')
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User(username, password)
            if user.register():
                flash('You have successfully told us your name and password! Now you can login.')
                return redirect(url_for('login'))
            else:
                flash('Username already exists.')
        return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username, password)
        if user.login():
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    flash("you have logged out, now you can log in again or register.")
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/users')
def users():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT rowid, * FROM users")

    rows = cur.fetchall()
    con.close()
    return render_template("users.html",rows=rows)


@app.route("/edit", methods=['POST','GET'])
def edit():
    rows = []
    if request.method == 'POST':
        id = request.form['id']
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row

        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id=?", (id,))

        rows = cur.fetchall()
        con.close()
        return render_template("edit.html", rows=rows)


@app.route("/editrec", methods=['POST','GET'])
def editrec():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        password = request.form['password']

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("UPDATE users SET username='"+name+"', password='"+password+"' WHERE rowid="+id)
            con.commit()
            flash("User has been successfully edited.")
        return render_template('home.html')


@app.route("/delete", methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        id = request.form['id']
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute("DELETE FROM users WHERE id=?", (id,))
            con.commit()
        flash("User has been successfully deleted.")
        return render_template('home.html')
    flash("Something went wrong, try again until it works.")
    return render_template('home.html')


@app.route('/addgame', methods=["POST", "GET"])
def addgame():
    if "username" in session:
        if request.method == 'POST':
            name = request.form['name']
            release_year = request.form['release_year']
            image_url = request.form['image_url']
            game = Game(name, release_year, image_url)
            if game.addgame():
                flash('You have successfully added your favorite game!')
                return redirect(url_for('fangames'))
        return render_template('addgame.html')
    else:
        flash("You have to login to add a game")
        return redirect(url_for("login"))



@app.route('/fangames')
def fangames():
    con = sqlite3.connect(DATABASE2, check_same_thread=False)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM games")
    user_games = cur.fetchall()
    con.close()
    return render_template('fangames.html', user_games=user_games)



if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    if not os.path.exists(DATABASE2):
        init_db2()
    app.run(debug=True)