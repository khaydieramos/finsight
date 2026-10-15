"""PostgreSQL persistence for synthetic FinSight transactions."""
import os
import pandas as pd
import psycopg
from psycopg.rows import dict_row

DDL = '''
CREATE TABLE IF NOT EXISTS transactions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    transaction_date DATE NOT NULL,
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    category TEXT NOT NULL CHECK (length(trim(category)) > 0),
    amount NUMERIC(14, 2) NOT NULL,
    UNIQUE (transaction_date, description, category, amount)
);
'''

def connection():
    url = os.getenv('DATABASE_URL')
    if not url:
        raise RuntimeError('DATABASE_URL is not set. See README.md.')
    return psycopg.connect(url)

def initialize():
    with connection() as conn:
        conn.execute(DDL)

def import_transactions(df):
    """Import validated data. Duplicate identical rows are skipped."""
    rows = [(row.date.date(), row.description, row.category, float(row.amount))
            for row in df.itertuples(index=False)]
    with connection() as conn:
        with conn.cursor() as cur:
            cur.executemany('''
                INSERT INTO transactions (transaction_date, description, category, amount)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (transaction_date, description, category, amount) DO NOTHING
            ''', rows)

def fetch_transactions():
    with connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute('''SELECT transaction_date AS date, description, category, amount
                           FROM transactions ORDER BY transaction_date, id''')
            rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=['date', 'description', 'category', 'amount'])
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = df['amount'].astype(float)
    return df
