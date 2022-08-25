import os
import psycopg2
import psycopg2.extras
import datetime
from functions import utc_to_ist, load

DATABASE_URL = os.environ["DATABASE_URL2"]
revivesAvailable = 3
"""
CREATE TABLE "members" (
	"id" BIGINT NOT NULL,
	"revives" INT,
	"last_used" TIMESTAMP,
	PRIMARY KEY ("id")
);
"""


class Database():

    def __init__(self, DATABASE_URL, tableName):
        self.DATABASE_URL = DATABASE_URL
        self.tableName = tableName

    def connect(self):
        self.conn = psycopg2.connect(self.DATABASE_URL)
        self.cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.DictCursor)
        return self.cursor

    def closeConnection(self):
        self.conn.commit()
        self.conn.close()


class Database_members(Database):

    def updateMember(self, person):
        sql = """UPDATE {}
        SET revives=%s,
            last_used=%s
        WHERE id=%s;
        """.format(self.tableName)
        cursor = self.connect()
        cursor.execute(sql,
                       (person.revives_available, person.last_used, person.id))
        self.closeConnection()

    def addMember(self, person):
        try:
            cursor = self.connect()
            sql = """INSERT INTO {} (id, revives, last_used)
    VALUES  (%s, %s, %s);""".format(self.tableName)
            cursor.execute(sql, (person.id, person.revives, person.last_used))
            self.closeConnection()
        except Exception as e:
            if type(e) == psycopg2.errors.UniqueViolation:
                try:
                    self.closeConnection()
                except:
                    print("Exception in exception")

    def resetRevives(self):
        sql = """UPDATE {}
        SET revives=%s;
        """.format(self.tableName)
        cursor = self.connect()
        cursor.execute(sql, (revivesAvailable, ))
        self.closeConnection()

    def resetRevivesUser(self, id):
        sql = """UPDATE {}
        SET revives=%s
        WHERE id=%s;""".format(self.tableName)
        cursor = self.connect()
        cursor.execute(sql, (revivesAvailable, id))
        self.closeConnection()

    def fetchUser(self, person):
        cursor = self.connect()
        cursor.execute("SELECT * from {} WHERE id=%s;".format(self.tableName),
                       (person.id, ))
        temp = cursor.fetchall()
        self.closeConnection()
        p1 = temp[0]
        person.last_used = p1[2]
        person.revives_available = p1[1]
        return (person)

    def viewAllUsers(self):
        cursor = self.connect()
        cursor.execute("SELECT * from {};".format(self.tableName))
        temp = cursor.fetchall()
        self.closeConnection()
        return (temp)

    def get_messages_lb(self, num=0, to_send=True):
        cursor = self.connect()
        cursor.execute(
            "SELECT id, messages_count FROM {} ORDER BY messages_count DESC;".
            format(self.tableName))
        allUsers = cursor.fetchall()
        self.closeConnection()

        if to_send == True:
            finalMsg = ''''''
            chunk = "<@{}> --- {}\n"

            if num == 0:
                for i in allUsers[:10]:
                    finalMsg += chunk.format(i[0], i[1])
            else:
                for i in allUsers[:num]:
                    finalMsg += chunk.format(i[0], i[1])
                return finalMsg
        else:
            return allUsers


class Database_message_bank():

    def __init__(self, DATABASE_URL, tableName):
        self.DATABASE_URL = DATABASE_URL
        self.tableName = tableName

        self.messages_total_count = 0
        self.update_after_count = 20

        self.cursor = self.connect()

    def connect(self):
        self.conn = psycopg2.connect(self.DATABASE_URL)
        self.cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.DictCursor)
        return self.cursor

    def closeConnection(self):
        self.conn.commit()
        self.conn.close()

    def get_data(self, date=None, to_send=True, num=10):
        if date == None:
            date = utc_to_ist(datetime.datetime.utcnow()).date()
        sql = f"SELECT id, count FROM {self.tableName} WHERE date=%s ORDER BY count DESC;"
        if self.cursor.closed == True:
            cursor = self.connect()
        else:
            cursor = self.cursor
        cursor.execute(sql, (date, ))
        allUsers = cursor.fetchall()

        if to_send == True:
            finalMsg = ''''''
            chunk = "<@{}> --- {:<4}\n"
            #"{:<18} {:<10} {:<4}"

            if num == 0:
                for i in allUsers[:10]:
                    finalMsg += chunk.format(i[0], i[1])
            else:
                for i in allUsers[:num]:
                    finalMsg += chunk.format(i[0], i[1])
                return finalMsg
        else:
            return allUsers

    def get_week_data(self, to_send=True, num=10, date_to_subtract=0):
        # SELECT id, sum(count) FROM message_bank WHERE date BETWEEN (current_date - 3) and current_date GROUP BY id;
        # SELECT id, sum(count) FROM message_bank WHERE date BETWEEN (current_date - CAST(EXTRACT(DOW FROM current_date) AS int)) and current_date GROUP BY id,count ORDER BY count DESC;
        sql = f"SELECT id, sum(count) FROM message_bank WHERE date BETWEEN (current_date-{date_to_subtract} - CAST(EXTRACT(DOW FROM current_date-{date_to_subtract}) AS int)) and current_date GROUP BY id ORDER BY SUM(count) DESC;"
        if self.cursor.closed == True:
            cursor = self.connect()
        else:
            cursor = self.cursor
        cursor.execute(sql)
        allUsers = cursor.fetchall()

        if to_send == True:
            finalMsg = ''''''
            chunk = "<@{}> --- {:<4}\n"
            #"{:<18} {:<10} {:<4}"

            if num == 0:
                for i in allUsers[:10]:
                    finalMsg += chunk.format(i[0], i[1])
            else:
                for i in allUsers[:num]:
                    finalMsg += chunk.format(i[0], i[1])
                return finalMsg
        else:
            return allUsers

    def get_week_activity(self, user_id):
        sql = "SELECT extract(dow from date) AS day, SUM(count) AS ganit FROM message_bank WHERE id=%s GROUP BY day ORDER BY ganit;"
        if self.cursor.closed == True:
            cursor = self.connect()
        else:
            cursor = self.cursor
        cursor.execute(sql, (user_id, ))
        data = cursor.fetchall()
        return data

    def insert_new_entry(self, idd, date, count):
        sql = """INSERT INTO {} (id, date, count) VALUES (%s, %s, %s);""".format(
            self.tableName)
        self.cursor.execute(sql, (idd, date, count))
        self.conn.commit()

    def update_message(self, idd, count):
        cursor = self.connect()
        sql = """UPDATE {}
        SET count = count + %s
        WHERE id=%s and date=%s;
        """.format(self.tableName)
        date = utc_to_ist(datetime.datetime.utcnow()).date()

        if self.cursor.closed == True:
            cursor = self.connect()

        cursor.execute(sql, (count, idd, date))

        if cursor.statusmessage == "UPDATE 1":
            self.conn.commit()
            self.messages_total_count += 1
        else:
            self.insert_new_entry(idd, date, count)
            self.messages_total_count += 1

        if self.messages_total_count > self.update_after_count:
            self.messages_total_count = 0


class Database_suggestions(Database):
    """
    CREATE TABLE "suggestions" (
	"message_id" BIGINT NOT NULL,
	"author_id" BIGINT NOT NULL,
    "resp" INT NOT NULL,
	PRIMARY KEY ("message_id","author_id")
    );
    """

    def fetch_interactions_id(self, message_id, resp):
        cursor = self.connect()
        cursor.execute(
            "SELECT * from {} WHERE message_id=%s AND resp=%s;".format(
                self.tableName), (message_id, resp))
        temp = cursor.fetchall()
        return temp

    def delete_message_id(self, message):
        cursor = self.connect()
        sql = """DELETE FROM {} WHERE message_id=%s;""".format(self.tableName)
        cursor.execute(sql, (message.id, ))
        self.closeConnection()

    def insert_message_id(self, message_id, user_id, resp):
        cursor = self.connect()
        sql = """INSERT INTO {} (message_id, author_id, resp) VALUES  (%s, %s, %s);""".format(
            self.tableName)
        cursor.execute(sql, (message_id, user_id, resp))
        self.closeConnection()


class Database_afk(Database):
    """
    CREATE TABLE "afk" (
	"id" BIGINT NOT NULL,
	"afk_status" BOOLEAN,
	"afk_time" TIMESTAMP,
	"content" TEXT,
	PRIMARY KEY ("id")
);
    """

    def get_all_afk(self):
        cursor = self.connect()
        cursor.execute("SELECT * from {}".format(self.tableName))
        temp = self.cursor.fetchall()
        self.closeConnection()
        return temp

    def remove_afk(self, author_id):
        cursor = self.connect()
        sql = """DELETE FROM {} WHERE id=%s;""".format(self.tableName)
        cursor.execute(sql, (author_id, ))
        self.closeConnection()

    def make_afk(self, message):
        text = message.content[5:]
        cursor = self.connect()
        sql = """INSERT INTO {} (id, afk_status, afk_time, content) VALUES  (%s, %s, %s, %s);""".format(
            self.tableName)
        cursor.execute(
            sql, (message.author.id, True, datetime.datetime.utcnow(), text))
        self.closeConnection()


class Database_guess(Database):
    """ CREATE TABLE "guess_scores" (
	"id" BIGINT NOT NULL,
	"score" INT NOT NULL,
	"played" INT NOT NULL,
	PRIMARY KEY ("id")
);
    """

    def get_lb(self):
        sql = "SELECT * FROM {} ORDER BY score DESC;"
        try:
            if self.cursor.closed is True:
                cursor = self.connect()
            else:
                cursor = self.cursor
        except:
            cursor = self.connect()
        cursor.execute(sql.format(self.tableName))
        temp = self.cursor.fetchall()
        return temp

    def get_score(self, idd):
        sql = "SELECT * FROM {} WHERE id=%s;"
        try:
            if self.cursor.closed is True:
                cursor = self.connect()
            else:
                cursor = self.cursor
        except:
            cursor = self.connect()
        cursor.execute(sql.format(self.tableName), (idd, ))
        temp = self.cursor.fetchall()
        return temp

    def insert_new_entry(self, idd, score, played=1):
        sql = """INSERT INTO {} (id, score, played) VALUES (%s, %s, %s);""".format(
            self.tableName)
        self.cursor.execute(sql, (idd, score, played))
        self.conn.commit()

    def update_score(self, idd, score, played=1):
        sql = """UPDATE {}
        SET score = score+ %s,
        played = played + %s
        WHERE id=%s;
        """.format(self.tableName)

        try:
            if self.cursor.closed is True:
                cursor = self.connect()
            else:
                cursor = self.cursor
        except:
            cursor = self.connect()

        cursor.execute(sql, (score, played, idd))

        if cursor.statusmessage == "UPDATE 1":
            self.conn.commit()
        else:
            self.insert_new_entry(idd, score, played=played)
