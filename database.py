import os
import psycopg2
import psycopg2.extras
import datetime
import pdb
from functions import utc_to_ist

DATABASE_URL = os.environ["DATABASE_URL2"]
revivesAvailable = os.environ["revives_available"]

"""
CREATE TABLE "members" (
	"id" BIGINT NOT NULL,
	"revives" INT,
	"last_used" TIMESTAMP,
	PRIMARY KEY ("id")
);
"""


class Database():
    def __init__(self,DATABASE_URL,tableName):
        self.DATABASE_URL = DATABASE_URL
        self.tableName = tableName
    def connect(self):
        self.conn = psycopg2.connect(self.DATABASE_URL)
        return self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    def closeConnection(self):
        self.conn.commit()
        self.conn.close()
    
    def updateMember(self, person):
        sql = """UPDATE {}
        SET revives=%s,
            last_used=%s
        WHERE id=%s;
        """.format(self.tableName)
        cursor = self.connect()
        cursor.execute(sql,(person.revives_available, person.last_used, person.id))
        self.closeConnection()

    def addMember(self,person):
        try:
            cursor = self.connect()
            sql = """INSERT INTO {} (id, revives, last_used)
    VALUES  (%s, %s, %s);""".format(self.tableName)
            cursor.execute(sql, (person.id, person.revives, person.last_used))
            self.closeConnection()
        except Exception as e:
            if type(e)==psycopg2.errors.UniqueViolation:
                try:
                    self.closeConnection()
                except:
                    print("Exception in exception")
    def resetRevives(self):
        sql = """UPDATE {}
        SET revives=%s;
        """.format(self.tableName)
        cursor = self.connect()
        cursor.execute(sql,(revivesAvailable, ))
        self.closeConnection()
    def fetchUser(self, person):
        cursor = self.connect()
        cursor.execute("SELECT * from {} WHERE id=%s;".format(self.tableName), (person.id, ))
        temp = cursor.fetchall()
        self.closeConnection()
        p1 = temp[0]
        person.last_used = p1[2]
        person.revives_available = p1[1]
        return(person)
    def viewAllUsers(self):
        cursor = self.connect()
        cursor.execute("SELECT * from {};".format(self.tableName))
        temp = cursor.fetchall()
        self.closeConnection()
        return(temp)
    def get_messages_lb(self, num=0, to_send=True):
        cursor = self.connect()
        cursor.execute("SELECT id, messages_count FROM {} ORDER BY messages_count DESC;".format(self.tableName))
        allUsers = cursor.fetchall()
        self.closeConnection()

        if to_send==True:
            finalMsg = ''''''
            chunk = "<@{}> --- {}\n"

            if num==0:
                for i in allUsers[:10]:
                    finalMsg+= chunk.format(i[0], i[1])
            else:    
                for i in allUsers[:num]:
                    finalMsg+= chunk.format(i[0], i[1])
                return finalMsg
        else:
            return allUsers
class DB_messages():
    def __init__(self,DATABASE_URL,tableName):
        self.DATABASE_URL = DATABASE_URL
        self.tableName = tableName

        self.messages_total_count = 0
        self.update_after_count = 20

    def connect(self):
        self.conn = psycopg2.connect(self.DATABASE_URL)
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        return self.cursor
    def closeConnection(self):
        self.conn.commit()
        self.conn.close()

    def insert_new_entry(self, idd, date, count):
        sql = """INSERT INTO {} (id, date, count) VALUES (%s, %s, %s);""".format(self.tableName)
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

        if cursor.statusmessage=="UPDATE 1":
            self.conn.commit()
            self.messages_total_count+=1
        else:
            self.insert_new_entry(idd, date, count)
            self.messages_total_count+=1

        if self.messages_total_count > self.update_after_count:
            self.messages_total_count = 0


def apppendMember(person):
    db = Database(DATABASE_URL, "members")
    db.addMember(person)        

#class Person():
#    def __init__(self):
#        self.id = 10 #302253506947973130
#        self.revives = 100
#        self.last_used = datetime.datetime.now()
#person = Person()

#db = DB_messages(DATABASE_URL, "message_bank")
#db.update_messages()
#print(db.fetchUser(person))
#db.addMember(person)
#x = (db.fetchUser(person))
#input(">")
#db.resetRevives()
