import datetime
import os

import discord
import ipdb
import psycopg2
import psycopg2.extras

from functions import load, utc_to_ist

creds = {'username': 'thewhistler', 'password': 'NavSrijan'}


def _is_connected(func):

    def wrapper(self, *args, **kwargs):
        if self.cursor.closed is True:
            # print("Connecting.")
            self.connect()
        else:
            # print("Already connected.")
            pass
        result = func(self, *args, **kwargs)
        self.conn.commit()
        return result

    return wrapper


class Database():
    database_name = "tc"

    def __init__(self, tableName):
        self.username = creds['username']
        self.password = creds['password']
        self.tableName = tableName
        self.connect()

    def connect(self):
        self.conn = psycopg2.connect(host="192.168.29.3",
                                     database=self.database_name,
                                     user=self.username,
                                     password=self.password)
        self.cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.DictCursor)
        return self.cursor

    def closeConnection(self):
        self.conn.commit()
        self.conn.close()

    @_is_connected
    def view_all(self):
        query = f"select * from {self.tableName};"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    @_is_connected
    def view_query(self, query, values=()):
        self.cursor.execute(query, values)
        result = self.cursor.fetchall()
        return result

    @_is_connected
    def view_where(self, where: tuple):
        query = f"select * from {self.tableName} where {where[0]}=%s;"
        self.cursor.execute(query, (where[1], ))
        result = self.cursor.fetchall()
        return result


class Message_Logs(Database):
    """CREATE TABLE "message_logs" (
        "message_id" BIGINT NOT NULL,
        "user_id" BIGINT NOT NULL,
        "channel_id" BIGINT NOT NULL,
        "time_of_message" TIMESTAMP NOT NULL,
        "content" TEXT NOT NULL,
        "mentions" BIGINT ARRAY NOT NULL,
        "word_count" INT NOT NULL,
        PRIMARY KEY ("message_id")
    );"""

    def __init__(self):
        tableName = "message_logs"
        super().__init__(tableName)

    @_is_connected
    def insert_message(self, message: discord.Message, word_count, emojis):
        query = f"""INSERT INTO {self.tableName}
        (message_id, user_id, channel_id, time_of_message, content, mentions, word_count, emojis)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        mentions = []
        for i in message.mentions:
            mentions.append(i.id)
        self.cursor.execute(query,
                            (message.id, message.author.id, message.channel.id,
                             message.created_at, message.content, mentions,
                             word_count, emojis))

    @_is_connected
    def get_week_activity(self, user_id):
        db = Message_Logs()
        query = f"SELECT extract(dow from time_of_message) AS day, SUM(word_count) AS ganit FROM {self.tableName} WHERE user_id=%s GROUP BY day ORDER BY ganit;"
        data = db.view_query(query, (user_id, ))
        return data

    @_is_connected
    def server_message_distribution(self):
        """Returns the number of messages sent in a day, grouped by hour."""
        query = f"select count(message_id), date_part('hour', time_of_message)  from {self.tableName} GROUP BY date_part('hour', time_of_message) ORDER BY date_part('hour', time_of_message);"
        messages = self.view_query(query)
        return messages

    @_is_connected
    def user_message_distribution(self, user_id):
        """Returns the number of messages sent bya a user in a day, grouped by hour."""
        query = f"select count(message_id), date_part('hour', time_of_message)  from {self.tableName} WHERE user_id=%s GROUP BY date_part('hour', time_of_message) ORDER BY date_part('hour', time_of_message);"
        messages = self.view_query(query, values=(user_id, ))
        return messages

    @_is_connected
    def lb_day(self, date=None, to_send=True, num=10):
        """Get the leaderboard for the day."""
        if date is None:
            date = utc_to_ist(datetime.datetime.utcnow()).date()
        query = f"SELECT user_id, SUM(word_count) AS wc FROM {self.tableName} where time_of_message::date=%s GROUP BY user_id ORDER BY wc DESC;"
        allUsers = self.view_query(query, values=(date, ))
        if to_send is True:
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

    @_is_connected
    def lb_week(self, date_to_subtract=0, to_send=True, num=10):
        """Get the leaderboard for the day."""
        query = f"SELECT user_id, sum(word_count) FROM message_logs WHERE time_of_message BETWEEN (current_date-{date_to_subtract} - CAST(EXTRACT(DOW FROM current_date-{date_to_subtract}) AS int)) and current_date GROUP BY user_id ORDER BY SUM(word_count) DESC;"
        allUsers = self.view_query(query, values=(date_to_subtract, ))
        if to_send is True:
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

    @_is_connected
    def average_character_count(self, user_id):
        """Average characters used by a user in his messages."""
        query = f"select AVG(LENGTH(content)) from {self.tableName} WHERE user_id=%s;"
        count = self.view_query(query, values=(user_id, ))
        return count

    @_is_connected
    def average_word_count(self, user_id):
        """Average words used by a user in his messages."""
        query = f"select AVG(word_count) from {self.tableName} WHERE user_id=%s;"
        count = self.view_query(query, values=(user_id, ))
        return count

    @_is_connected
    def mentioned(self, user_id):
        """Returns who a particular user mentions."""
        query = f"select unnest(mentions) as men, count(message_id) AS jj from {self.tableName} WHERE user_id=%s GROUP BY men ORDER BY jj DESC;"
        mentions = self.view_query(query, values=(user_id, ))
        return mentions

    @_is_connected
    def mentioned_by(self, user_id):
        """Returns who mentions a particular user."""
        query = f"select user_id, count(user_id) from {self.tableName} where %s = ANY(mentions) GROUP BY user_id;"
        mentions = self.view_query(query, values=(user_id, ))
        return mentions

    @_is_connected
    def most_used_emojis_user(self, user_id):
        """Returns which emojis a user uses."""
        query = f"select unnest(emojis) as men, count(message_id) AS jj from {self.tableName} WHERE user_id=%s GROUP BY men ORDER BY jj DESC;"
        mentions = self.view_query(query, values=(user_id, ))
        return mentions

    @_is_connected
    def most_used_emojis_server(self):
        """Returns which emojis are being used the most."""
        query = f"select unnest(emojis) as men, count(message_id) AS jj from {self.tableName} GROUP BY men ORDER BY jj DESC;"
        mentions = self.view_query(query)
        return mentions

    @_is_connected
    def fetch_messages(self, user_id, n=10000):
        """Fetch n number of messages of a user."""
        query = f"select content from {self.tableName} where user_id=%s ORDER BY time_of_message DESC LIMIT {n};"
        result = self.view_query(query, values=(user_id, ))
        return result

    @_is_connected
    def search_messages(self, string_to_search):
        """Returns message IDs of messages with certain string."""
        query = f"SELECT message_id FROM {self.tableName} WHERE position(%s in content)>0 ORDER BY time_of_message DESC;"
        mentions = self.view_query(query, values=(string_to_search, ))
        return mentions


class Afk(Database):
    """
    CREATE TABLE afk (
    "user_id" BIGINT NOT NULL,
    "afk_status" BOOLEAN,
    "afk_time" TIMESTAMP,
    "content" TEXT,
    PRIMARY KEY(user_id));
    """

    def __init__(self):
        tableName = "afk"
        super().__init__(tableName)

    @_is_connected
    def get_all_afk(self):
        temp = self.view_all()
        return temp

    @_is_connected
    def remove_afk(self, author_id):
        sql = """DELETE FROM {} WHERE user_id=%s;""".format(self.tableName)
        self.cursor.execute(sql, (author_id, ))

    @_is_connected
    def make_afk(self, message):
        text = message.content[5:]
        sql = """INSERT INTO {} (user_id, afk_status, afk_time, content) VALUES  (%s, %s, %s, %s);""".format(
            self.tableName)
        self.cursor.execute(
            sql, (message.author.id, True, datetime.datetime.utcnow(), text))


class Database_suggestions(Database):
    """
    CREATE TABLE "suggestions" (
	"message_id" BIGINT NOT NULL,
	"author_id" BIGINT NOT NULL,
    "resp" INT NOT NULL,
	PRIMARY KEY ("message_id","author_id")
    );
    """

    @_is_connected
    def fetch_interactions_id(self, message_id, resp):
        self.cursor.execute(
            "SELECT * from {} WHERE message_id=%s AND resp=%s;".format(
                self.tableName), (message_id, resp))
        temp = self.cursor.fetchall()
        return temp

    @_is_connected
    def delete_message_id(self, message):
        sql = """DELETE FROM {} WHERE message_id=%s;""".format(self.tableName)
        self.cursor.execute(sql, (message.id, ))

    @_is_connected
    def insert_message_id(self, message_id, user_id, resp):
        sql = """INSERT INTO {} (message_id, author_id, resp) VALUES  (%s, %s, %s);""".format(
            self.tableName)
        self.cursor.execute(sql, (message_id, user_id, resp))


class Database_guess(Database):
    """ CREATE TABLE "guess_scores" (
	"id" BIGINT NOT NULL,
	"score" INT NOT NULL,
	"played" INT NOT NULL,
	PRIMARY KEY ("id")
);
    """

    @_is_connected
    def get_lb(self):
        sql = "SELECT * FROM {} ORDER BY score DESC;"
        self.cursor.execute(sql.format(self.tableName))
        temp = self.cursor.fetchall()
        return temp

    @_is_connected
    def get_score(self, idd):
        sql = "SELECT * FROM {} WHERE id=%s;"
        self.cursor.execute(sql.format(self.tableName), (idd, ))
        temp = self.cursor.fetchall()
        return temp

    @_is_connected
    def insert_new_entry(self, idd, score, played=1):
        sql = """INSERT INTO {} (id, score, played) VALUES (%s, %s, %s);""".format(
            self.tableName)
        self.cursor.execute(sql, (idd, score, played))

    @_is_connected
    def update_score(self, idd, score, played=1):
        sql = """UPDATE {}
        SET score = score+ %s,
        played = played + %s
        WHERE id=%s;
        """.format(self.tableName)

        self.cursor.execute(sql, (score, played, idd))

        if self.cursor.statusmessage == "UPDATE 1":
            pass
        else:
            self.insert_new_entry(idd, score, played=played)


db = Message_Logs()