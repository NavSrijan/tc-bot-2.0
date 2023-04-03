import datetime
import os
from collections import Counter, OrderedDict

import discord
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
        """Get the leaderboard for the week."""

        query = f"SELECT user_id, sum(word_count) FROM message_logs WHERE time_of_message BETWEEN (current_date-{date_to_subtract} - CAST(EXTRACT(DOW FROM current_date-{date_to_subtract}) AS int)) and current_date+1 GROUP BY user_id ORDER BY SUM(word_count) DESC;"
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
    def lb_week_combined(self, date_to_subtract=0):
        """Get combined lb of both voice and message logs"""
        query = """
        SELECT COALESCE(ml.user_id, vl.user_id), CAST(0.3*COALESCE(vl.ts,0)+COALESCE(ml.wc,0) AS INT) AS ss
            FROM (
            SELECT 
                user_id, sum(time_spent) as ts
            FROM 
                voice_logs
            WHERE 
                time_of_update 
                BETWEEN (current_date-0 - CAST(EXTRACT(DOW FROM current_date-0) AS int)) 
                and
                current_date +1
            GROUP BY 
                user_id 
            ) AS vl
            FULL OUTER JOIN 
            (SELECT 
                user_id, sum(word_count) as wc
            FROM 
                message_logs
            WHERE 
                time_of_message 
                BETWEEN (current_date-0 - CAST(EXTRACT(DOW FROM current_date-0) AS int)) 
                and
                current_date +1
            GROUP BY 
                user_id 
            ) ml ON ml.user_id=vl.user_id
            ORDER BY ss DESC
        """
        allUsers = self.view_query(query, values=(date_to_subtract, ))
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
        return count[0][0]

    @_is_connected
    def mentioned_user(self, user_id, u2):
        """Returns who a particular user mentions."""
        query = f"select count(message_id) from {self.tableName} WHERE user_id=%s and %s=ANY(mentions);"
        mentions = self.view_query(query, values=(user_id, u2))
        return mentions[0][0]

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
    def random_active_user(self, days=7):
        """Fetch a random active user."""
        query = f"SELECT DISTINCT user_id FROM {self.tableName} WHERE time_of_message>(now() -INTERVAL '{days} DAY');"
        result = self.view_query(query)
        return result

    @_is_connected
    def search_messages(self, string_to_search):
        """Returns message IDs of messages with certain string."""
        query = f"SELECT message_id FROM {self.tableName} WHERE position(%s in content)>0 ORDER BY time_of_message DESC;"
        mentions = self.view_query(query, values=(string_to_search, ))
        return mentions

    @_is_connected
    def check_for_revive(self):
        query = f"SELECT COUNT(message_id) AS mi, user_id FROM {self.tableName} WHERE time_of_message BETWEEN NOW() - INTERVAL '20 mins' AND NOW() GROUP BY user_id ORDER BY mi DESC;"
        res = self.view_query(query)
        return res


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

    def __init__(self):
        tableName = "guess_scores"
        super().__init__(tableName)

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


class Command_Logs(Database):
    """
    CREATE TABLE "command_logs" (
	"id" serial primary key,
	"user_id" BIGINT,
	"command" TEXT,
	"arguments" JSON,
	"time_of_command" TIMESTAMP
);
    """

    def __init__(self):
        tableName = "command_logs"
        super().__init__(tableName)

    @_is_connected
    def insert_command(self, message, message_id, command, args, user):
        query = f"""INSERT INTO {self.tableName} (message_id, user_id, command, arguments, time_of_command) VALUES(%s, %s, %s, %s, %s);"""
        self.cursor.execute(
            query, (message_id, user.id, command, args, message.created_at))


class Voice_Logs(Database):
    """
CREATE TABLE "voice_logs" (
	"id" SERIAL,
	"user_id" BIGINT,
	"channel_id" BIGINT,
	"event" INT,
	"deaf" BOOLEAN,
	"mute" BOOLEAN,
	"self_mute" BOOLEAN,
	"self_deaf" BOOLEAN,
	"self_stream" BOOLEAN,
	"self_video" BOOLEAN,
	"afk" BOOLEAN,
	"time_of_update" TIMESTAMP,
	"time_spent" INT
);
    """

    def __init__(self):
        tableName = "voice_logs"
        super().__init__(tableName)

    @_is_connected
    def fetch_last_state(self, user_id):
        query = f"SELECT * FROM {self.tableName} WHERE user_id=%s ORDER BY time_of_update DESC LIMIT 1;"
        data = self.view_query(query, (user_id, ))
        return data[0]

    @_is_connected
    def insert_command(self, member_id, channel_id, voice_state, event, time_spent):
        """
        event
        0: leave
        1: join
        """
        query = f"""INSERT INTO {self.tableName} (user_id, channel_id, event, deaf, mute, self_mute, self_deaf, self_stream, self_video, afk, time_of_update, time_spent) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        self.cursor.execute(
            query,
            (member_id, channel_id, event, voice_state.deaf, voice_state.mute,
             voice_state.self_mute, voice_state.self_deaf,
             voice_state.self_stream, voice_state.self_video, voice_state.afk,
             datetime.datetime.now(), time_spent))

    @_is_connected
    def lb_week(self, date_to_subtract=0):
        """Get the leaderboard for the week."""

        query = f"SELECT user_id, sum(time_spent) FROM voice_logs WHERE time_of_update BETWEEN (current_date-{date_to_subtract} - CAST(EXTRACT(DOW FROM current_date-{date_to_subtract}) AS int)) and current_date+1 GROUP BY user_id ORDER BY SUM(time_spent) DESC;"
        allUsers = self.view_query(query, values=(date_to_subtract, ))
        return allUsers

class Birthday(Database):
    """
    CREATE TABLE "birthday" (
        "user_id" BIGINT NOT NULL,
        "birthdate" DATE NOT NULL,
        PRIMARY KEY ("user_id")
    );
    """

    def __init__(self):
        tableName = "birthday"
        super().__init__(tableName)

    @_is_connected
    def insert_command(self, user_id, birthdate):
        query = f"""INSERT INTO {self.tableName} (user_id, birthdate) VALUES(%s, %s) ON CONFLICT (user_id) DO UPDATE SET birthdate=%s;"""
        self.cursor.execute(
            query, (user_id, birthdate, birthdate))

    @_is_connected
    def remove_command(self, user_id):
        query = f"""DELETE FROM {self.tableName} WHERE user_id={user_id};"""
        self.cursor.execute(query, (user_id, ))

    @_is_connected
    def get_todays_birthdays(self):
        query = f"SELECT * FROM {self.tableName} WHERE	DATE_PART('day', birthdate) = DATE_PART('day', CURRENT_DATE)AND DATE_PART('month', birthdate) = DATE_PART('month', CURRENT_DATE)"
        vals = self.view_query(query)
        return vals

    @_is_connected
    def get_upcoming_birthdays(self, n=10):
        """Returns upcoming birthdays for the next 3 months."""
        query = f"""with next_3_months as (select (select to_char(x::date, 'MM-DD' )) md from generate_series(now(), now() + '3 months'::interval, '1 day'::interval) x)
select
   b.*
FROM
   next_3_months n5d
   join {self.tableName} b on n5d.md = (select to_char( b.birthdate, 'MM-DD' ));"""
        vals = self.view_query(query)
        return vals

    @_is_connected
    def get_age(self, user_id):
        #query = f"select AGE(birthdate) from {self.tableName};"
        query = f"SELECT birthdate from {self.tableName} where user_id=%s"
        result = self.view_query(query, values=(user_id, ))
        return result



class Synergy():

    def __init__(self, u1, u2):
        self.u1 = u1
        self.u2 = u2
        self.ml = Message_Logs()

        #Executing steps
        self.step_1()
        self.step_2()
        self.step_3()
        self.step_4()
        self.step_5()

        self.finalize_data()

    def split_words(self, messages):
        ll = []
        not_these_words = [
            "is", "the", "a", "an", "was", "there", "their", "i"
        ]
        not_these_words = []
        for i in messages:
            k = i[0]
            if k.startswith("http"):
                continue
            ss = k.split()
            for j in ss:
                if j.lower() not in not_these_words:
                    ll.append(j.lower())
        return ll

    def step_1(self):
        """
        Find the common words used by both.
        """

        # Prepare the data set
        user1 = self.ml.fetch_messages(self.u1, n=1000)
        user2 = self.ml.fetch_messages(self.u2, n=1000)
        self.u1_words = self.split_words(user1)
        self.u2_words = self.split_words(user2)

        total = 30
        u1 = Counter(self.u1_words).most_common()[:total]
        u2 = Counter(self.u2_words).most_common()[:total]

        ll = [[], []]
        p = 0
        for k in [u1, u2]:
            for i in k:
                ll[p].append(i[0])
            p += 1

        u1_l, u2_l = ll

        # Now finding the intersection
        final_dataset = set(u1_l) & set(u2_l)

        # Generating a percentage
        total_to_consider = 0.6 * total
        final = (len(final_dataset) * 100) / total_to_consider
        if final > 100:
            final = 100

        self.step_1_data = {'score': final, 'words': final_dataset}
        return self.step_1_data

    def step_2(self):
        """
        Calculating the common hours in the day.
        """
        u1 = self.ml.user_message_distribution(self.u1)
        u2 = self.ml.user_message_distribution(self.u2)
        u1 = sorted(u1, key=lambda x: x[0], reverse=True)
        u2 = sorted(u2, key=lambda x: x[0], reverse=True)

        res = [[], []]
        p = 0
        # Convert the times provided in a suitable format.
        for i in [u1, u2]:
            for j in i:
                res[p].append(j[1])
            p += 1
        u11, u22 = res

        # Getting the common hours between the two parties
        total = 5
        common_hours = set(u11[:total]) & set(u22[:total])
        percentage_hours = len(common_hours) * 100 / (total)

        data1 = self.ml.get_week_activity(self.u1)[:3]
        data2 = self.ml.get_week_activity(self.u2)[:3]

        days = [
            "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
            "Saturday"
        ]

        res = [[], []]
        p = 0
        for i in [data1, data2]:
            for j in i:
                res[p].append(days[int(j[0])])
            p += 1
        data1, data2 = res
        total = 3
        common_days = set(data1) & set(data2)
        percentage_day = len(common_days) * 100 / (total)

        self.step_2_data = {
            'score': (percentage_day + percentage_hours) / 2,
            'score_hours': percentage_hours,
            'common_hours': list(common_hours),
            'score_days': percentage_day,
            'common_days': list(common_days),
            'top_hour_1': u11[0],
            'top_hour_2': u22[0],
            'top_day_1': data1[0],
            'top_day_2': data2[0]
        }

    def step_3(self):
        """
        Mention and Mentioned by ratio
        """
        u2_men_by_u1 = self.ml.mentioned_user(self.u1, self.u2)
        u1_men_by_u2 = self.ml.mentioned_user(self.u2, self.u1)
        ll = [u2_men_by_u1, u1_men_by_u2]

        a, b = min(ll), max(ll)

        score = (a / b) * 100
        self.step_3_data = {
            'score': score,
            'u2_men_by_u1': u2_men_by_u1,
            'u1_men_by_u2': u1_men_by_u2
        }

    def step_4(self):
        """
        Emoji matcher
        """
        u1 = self.ml.most_used_emojis_user(self.u1)
        u2 = self.ml.most_used_emojis_user(self.u2)

        common_emojis = []

        for index, emoji in enumerate(u1[:20]):
            for index_2, emoji_2 in enumerate(u2[:20]):
                if emoji[0] == emoji_2[0]:
                    common_emojis.append((emoji[0], emoji[1], emoji_2[1]))

        def similarity_percentage(a, b):
            ll = [a, b]
            a = min(ll)
            b = max(ll)

            return (a / b) * 100

        total_percentage = 0

        for i in common_emojis:
            total_percentage += similarity_percentage(i[1], i[2])

        total_percentage = total_percentage / len(common_emojis)

        self.step_4_data = {
            'score': total_percentage,
            'u1_emojis': u1,
            'u2_emojis': u2,
            'common_emojis': common_emojis
        }
        return self.step_4_data

    def step_5(self):
        """
        Avg. length of a message.
        """
        u1 = self.ml.average_word_count(self.u1)
        u2 = self.ml.average_word_count(self.u2)

        diff = abs(u1-u2)
        mean = (u1+u2)/2
        percent = 100-diff*100/mean

        self.step_5_data = {'score': float(percent), 'difference': float(diff), 'u1_wc':float(u1), 'u2_wc':float(u2)}

    def finalize_data(self):
        score1 = self.step_1_data['score']
        score2 = self.step_2_data['score']
        score3 = self.step_3_data['score']
        score4 = self.step_4_data['score']
        score5 = self.step_5_data['score']

        self.final_score = (score1 + score2 + score3 + score4 + score5)/5

db = Message_Logs()
