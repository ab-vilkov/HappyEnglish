from flask import Flask, request, render_template
import sqlite3 as sq
from urllib.request import urlopen
from urllib.error import HTTPError
import re

app = Flask(__name__)



@app.route("/")
def index():
    q = request.args.get("q")
    if q is None:
        return render_template("index.html")
    if q == "":
        return render_template("index.html")
    db = sq.connect("Happy_English_1_2.db")
    cur = db.cursor()
    rows = cur.execute("SELECT * FROM subs WHERE content LIKE ?", (f'% {q} %',)).fetchall()

    u = unique_videos(rows)
    if u is None:
        return render_template("error.html")
    if len(u) == 0:
        return render_template("error.html")
    if len(u) == 1:
        u = rows
    res = generate_ansver(u)
    db.close()
    if len(res) == 0:
        return render_template("error.html")
    t = render_template("ansver.html", result=res)
    return t


def generate_ansver(ansver):
    if len(ansver) > 10:
        ansver = ansver[:11]
    result = []
    for row in ansver:
        db = sq.connect("Happy_English_1_2.db")
        cur = db.cursor()
        id = row[0]
        link = cur.execute("SELECT link FROM video WHERE videoID=?", (id,)).fetchall()[0][0]
        if link == "":
            link = get_link_video_from_ted(id)
            if link == "":
                continue
        link += f'#t={row[4]//1000},{(row[4]//1000) + (row[1]//1000+4)}'
        result.append([link, row[2]])
    # print(result)
    return result

def unique_videos(rows):
    if len(rows) == 0:
        return None
    if len(rows) == 1:
        return rows
    prev = rows[0][0]
    ansver = [rows[0]]
    for row in rows[1:]:
        if row[0] == prev:
            continue
        ansver.append(row)
        prev = row[0]
    return ansver

def get_link_video_from_ted(id:int):
    try:
        url_ted_opened = urlopen(f"https://www.ted.com/talks/{id}")
    except HTTPError as e:
        # print("error", id)
        return ""
    response = url_ted_opened.read().decode("utf8")
    c = re.findall("https:\/\/py\.tedcdn\.com\/.*?\.mp4", response)
    if len(c) > 0:
        return c[0]
    # print(c)
    return ""



if __name__ == '__main__':
    app.run(debug=False)