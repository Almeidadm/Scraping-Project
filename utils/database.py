import sqlite3


class DataBaseConnector:

    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None

    def fetch_data(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_table(self):
        query = '''
        CREATE TABLE IF NOT EXISTS products (
            title TEXT,
            price REAL,
            url TEXT UNIQUE,
            website TEXT
        )
        '''
        self.connection.execute(query)

    def insert_data(self, data_frame):
        cursor = self.connection.cursor()
        cursor.execute("BEGIN TRANSACTION")
        query = '''
            INSERT OR IGNORE INTO products (title, price, url, website)
            VALUES (?, ?, ?, ?)
            '''
        data = [(row['title'], row['price'], row['url'], row['website']) for _, row in data_frame.iterrows()]
        cursor.executemany(query, data)

        self.connection.commit()
