import sqlite3


class ProductDAO:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, timeout=10)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            xpath TEXT NOT NULL,
            price REAL,
            UNIQUE(title, url)
        )
        ''')
        self.conn.commit()

    def bulk_insert_or_update(self, products: list):
        cursor = self.conn.cursor()
        data = [(p['title'], p['url'], p['xpath'], p['price']) for p in products]
        cursor.executemany('''
        INSERT INTO products (title, url, xpath, price) 
        VALUES (?, ?, ?, ?)
        ON CONFLICT(title, url) DO UPDATE SET price=excluded.price, xpath=excluded.xpath
        ''', data)
        self.conn.commit()

    def close(self):
        self.conn.close()
