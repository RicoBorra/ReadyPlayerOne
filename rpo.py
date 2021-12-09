from flask import Flask, render_template, request, make_response
from threading import Thread
from threading import Lock
from hashlib import sha256
import sqlite3
lock = Lock()
con = sqlite3.connect("data.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS data (id INT, round INT, p1s INT, p2s INT)")
cur.execute("INSERT INTO data VALUES (0, 0, 0, 0)")
con.commit()
con.close()

app = Flask(__name__)
WINNING_SCORE = 5

def add_data(id, p1s, p2s):
    with lock:
        con = sqlite3.connect("data.db")
        cur = con.cursor()
        round = cur.execute("SELECT id, round FROM data WHERE id=? ORDER BY round DESC LIMIT 1", (id,)).fetchone()[1] + 1
        cur.execute("INSERT INTO data VALUES (?, ?, ?, ?)", (id, round, p1s, p2s))
        con.commit()
        con.close()
    return

def check(id: int): #controlli anti cheat
    with lock:
        con = sqlite3.connect("data.db")
        cur = con.cursor()
        data = cur.execute("SELECT * FROM data WHERE id=? ORDER BY round DESC LIMIT 5", (id,)).fetchall()
        con.commit()
        con.close()
    if ((data[0][2] != WINNING_SCORE) or (len(data) < WINNING_SCORE)):
        return False
    for i in range(0, len(data)-1):
        diff1 = data[i][2] - data[i+1][2]
        diff2 = data[i][3] - data[i+1][3]
        if ((diff1 > 1 or diff2 > 1) or (diff1 < 0 or diff2 < 0) or (diff1 + diff2 > 1)):
            return False
    return True

def aggiungi_id(resp):
    with lock:
        con = sqlite3.connect("data.db")
        cur = con.cursor()
        id = cur.execute("SELECT id FROM data ORDER BY id DESC LIMIT 1").fetchone()[0] + 1
        cur.execute("INSERT INTO data VALUES (?, 0, 0, 0)", (id,))
        con.commit()
        con.close()
    resp.set_cookie('userID', str(id))
    string = "fumozatla" + str(id)
    resp.set_cookie('hashish', sha256(string.encode()).hexdigest())
    return

@app.route("/")
def game():
    resp = make_response(render_template("readyplayerone.html"))
    try:
        id = int(request.cookies.get("userID"))
    except:
        aggiungi_id(resp)
    return resp

@app.route("/data", methods = ['POST'])
def data():
    data = request.form
    try:
        id = int(request.cookies.get("userID"))
    except Exception as e:
        return "ko"
    try:
        string = "fumozatla" + str(id)
        if request.cookies.get("hashish") == sha256(string.encode()).hexdigest():
            add_data(id, int(data.get('p1s')), int(data.get('p2s')))
    except Exception as e:
        print(e)
        pass
    return "ok"

@app.route("/verify")
def verify():
    try:
        id = int(request.cookies.get("userID"))
        if check(id):
            string = "fumozatla" + str(id)
            try:
                if request.cookies.get("hashish") != sha256(string.encode()).hexdigest():
                    return "No stealing plz..."
            except:
                return "No stealing plz..."
            return "ptm{1_l1k3d_w0nd3rw4ll}"
    except Exception as e:
        print(e)
        pass
    return "Something went wrong"

if __name__ == "__main__":
    app.run(host = "0.0.0.0", debug=False)
