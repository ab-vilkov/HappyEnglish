import re
import sqlite3 as sq
import json
from urllib.request import urlopen
from urllib.error import HTTPError


def ted_get_json(id: int, lang="en"):
    try:
        url_ted_opened = urlopen(f"https://www.ted.com/talks/subtitles/id/{id}/lang/{lang}")

    except HTTPError as e:
        return ""

    ted_dits = json.loads(url_ted_opened.read().
                          decode("utf8"))["captions"]
    return ted_dits


def get_link_video_from_ted(id:int):
    try:
        url_ted_opened = urlopen(f"https://www.ted.com/talks/{id}")
    except HTTPError as e:
        print("error", id)
        return ""
    response = url_ted_opened.read().decode("utf8")
    c = re.findall("https:\/\/py\.tedcdn\.com\/.*?\.mp4", response)
    if len(c) > 0:
        return c[0]
    # print(c)
    return ""


class Db:
    name : str
    connection: sq.Connection
    cur : sq.Cursor

    def __init__(self, connection: sq.Connection):
        self.connection = connection
        self.cur = self.connection.cursor()

    # def create_table(self, tables : dict):
    #     for table in tables.keys():
    #         self.cur.execute()
    #         for k, v in tables[table].items():
    #             self.cur.execute('''ALTER TABLE {}
    #             ADD {} {}'''.format(table, k, v))
    #     self.connection.commit()

    def insert_subs_into_db(self, table, dicts, id):
        for indict in dicts:
            # print([id] + list(indict.values()))
            tmp = [id] + list(indict.values())
            # print(tmp)
            self.connection.execute(f'''INSERT INTO {table}
            VALUES (?, ?, ?, ?, ?)''', tmp)


    def insert_new_video_into_db(self, id, link):
        self.cur.execute("INSERT INTO video VALUES (?, ?)", [id] + [link])



db = Db(sq.connect("Happy_English_1_2.db"))

tables = {"subs": {"duration": "integer", "content": "text", "startOfParagraph": "integer",
                   "startTime": "integer"}}
#
# db.cur.execute("CREATE TABLE video (videoID integer PRIMARY KEY NOT NULL, link text)")
# db.cur.execute("CREATE TABLE subs (id integer NOT NULL, duration integer, content text,startOfParagraph integer,startTime integer, FOREIGN KEY(id) REFERENCES videos (id));")
# db.connection.commit()
# db.cur.close()

for i in range(8947, 15000):
    db.connection = sq.connect("Happy_English_1_2.db")
    db.cur = db.connection.cursor()
    dicts = ted_get_json(i)
    if dicts != "":
        link = get_link_video_from_ted(i)
        db.insert_new_video_into_db(i, link)
        db.insert_subs_into_db("subs", dicts, i)
        db.connection.commit()
        db.cur.close()
    print(i, "done")


# c = db.cur.execute("SELECT id FROM subs").fetchall()
# for i in c:
#     id = i[0]
#     link = get_link_video_from_ted(id)
#     if link != "":
#         # print(f'''INSERT INTO video (link) VALUES ({link}) WHERE videoID={id}''')
#         db.cur.execute(f'''INSERT INTO video (link)
#          VALUES (?)
#           SELECT videoID FROM video WHERE videoID=(?)''', [link] + [id])


print()


# get_data_from_ted(3)





