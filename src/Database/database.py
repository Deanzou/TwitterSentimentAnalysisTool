import psycopg2
from src.Obj.tweet import Tweet
from src.Obj.tweetlist import TweetList


# Class Database: Adds and removes objects from postgres
class Database:
    # constructor to initialize connection
    def __init__(self, user, password, host, port):
        self.connection = psycopg2.connect(user=user, password=password, host=host, port=port)
        self.cursor = self.connection.cursor()
        self.cursor.execute("SELECT version();")
        record = self.cursor.fetchone()
        print("You are connected to - ", record)

    # destructor to commit changes to database
    def __del__(self):
        self.connection.commit()
        self.connection.close()
        self.cursor.close()

    # Creates a table with name `name` consisting of a set of column names and
    # types. The number of column names and types must be equivalent.
    def create_table(self, name, column_name, column_type):
        if len(column_name) != len(column_type):
            raise ValueError("column names must match size of column types")
        table_command = "CREATE TABLE " + name + " ("
        for i in range(len(column_name)):
            table_command += column_name[i] + " " + column_type[i] + ", "
        table_command = table_command[:-2]
        table_command += ");"
        self.cursor.execute(table_command)

    # Returns number of rows in a specific column
    def num_rows(self, table_name, column_name):
        table_command = "SELECT COUNT(" + column_name + ") FROM " + table_name
        return self.cursor.execute(table_command)

    # updates a column based on id
    def update_column_by_id(self, table_name, column_name, tweet_id, new_value):
        table_command = "UPDATE " + table_name + " SET " + column_name + " = " + str(new_value) + \
                        " WHERE id = " + str(tweet_id)
        self.cursor.execute(table_command)

    def update_column_by_text(self, table_name, column_name, text, new_value):
        table_command = "UPDATE " + table_name + " SET " + column_name + " = '" + str(new_value) + \
                        "' WHERE text = " + "'{0}'".format(text)
        self.cursor.execute(table_command)

    # creates a new column and adds data in form of a data object to it into it
    def create_column(self, table_name, column_name, data, type_data):
        table_command = "ALTER TABLE " + table_name + " ADD COLUMN " + column_name + " " + type_data
        self.cursor.execute(table_command)
        self.insert_list(table_name, column_name, data)

    # deletes a row
    def delete_row(self, table_name, tweet_id):
        table_command = "DELETE FROM " + table_name + " WHERE id =" + str(tweet_id)
        self.cursor.execute(table_command)

    # gets column data and returns as list
    def get_column_data(self, table_name, column_name):
        table_command = "SELECT " + column_name + " FROM " + table_name
        self.cursor.execute(table_command)
        return self.cursor.fetchall()

    # gets row data and returns it as a tweet
    def get_row_data(self, table_name, tweet_id):
        table_command = "SELECT * FROM " + table_name + " WHERE id = " + str(tweet_id)
        self.cursor.execute(table_command)
        return self.cursor.fetchall()

    # inserts a tweet object into a table
    def insert_tweet(self, table_name, tweet_id, tweet):
        table_command = "INSERT into {0}" \
                        " VALUES ({1}, '{2}', '{3}', {4}, {5}, {6}, '{7}', '{8}', '{9}')".format(table_name,
                                                                                                 str(tweet_id),
                                                                                                 self.check_none(
                                                                                                     tweet.text).replace(
                                                                                                     "'", ""),
                                                                                                 self.check_none(
                                                                                                     tweet.user),
                                                                                                 self.check_none(
                                                                                                     tweet.retweet_count),
                                                                                                 self.check_none(
                                                                                                     tweet.favorite_count),
                                                                                                 self.check_none(
                                                                                                     tweet.follower_count),
                                                                                                 self.check_none(
                                                                                                     tweet.date),
                                                                                                 self.check_none(
                                                                                                     tweet.nlp_score),
                                                                                                 self.check_none(
                                                                                                     tweet.given_score))
        self.cursor.execute(table_command)

    # inserts a list of tweet objects
    def insert_tweet_list(self, table_name, tweet_list):
        for value in tweet_list.data:
            self.insert_tweet(table_name, value, tweet_list.data[value])

    # inserts a general list
    def insert_list(self, table_name, column_name, list):
        for value in list:
            # noinspection PyBroadException
            try:
                value = value.replace("'", "")
            except Exception:
                pass
            table_command = "INSERT into {0} ({1}) VALUES ('{2}')".format(table_name, column_name, value)
            self.cursor.execute(table_command)

    # helper method for insert_data
    @staticmethod
    def check_none(value):
        if value is None:
            return "-10"
        else:
            return value

    # commits to db (used for testing, optimally destructor will commit)
    def commit(self):
        self.connection.commit()

    # gets the number of columns of a table
    def get_num_of_columns(self, name):
        table_command = "SELECT COUNT(*) FROM " + name
        self.cursor.execute(table_command)
        return self.cursor.fetchone()[0]

    # parses the table of tweets back into a tweet_list obj usable in plots
    def parse_db_into_tweet_list(self, name):
        num_cols = self.get_num_of_columns(name)
        tweet_list = TweetList()
        for tweet_id in range(1, num_cols + 1):
            tweet = Tweet()
            unparsed_data = self.get_row_data(name, tweet_id)
            try:
                unparsed_data = unparsed_data[0]
            except IndexError:
                continue

            tweet.add_tweet(unparsed_data[1], unparsed_data[2], unparsed_data[3], unparsed_data[4], unparsed_data[5],
                            unparsed_data[6], unparsed_data[7], unparsed_data[8], unparsed_data[9])
            tweet_list.insert_data(tweet)
        return tweet_list
