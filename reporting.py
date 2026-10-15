"""SQL-powered financial reporting for FinSight (PostgreSQL mode)."""
import pandas as pd
from db import connection

MONTHLY_SQL = """
SELECT DATE_TRUNC('month', transaction_date)::date AS month,
       COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) AS income,
       COALESCE(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 0) AS expenses,
       COALESCE(SUM(amount), 0) AS net
FROM transactions
WHERE transaction_date BETWEEN %s AND %s
GROUP BY DATE_TRUNC('month', transaction_date)
ORDER BY month
"""

CATEGORY_SQL = """
SELECT category, SUM(-amount) AS spent
FROM transactions
WHERE amount < 0 AND transaction_date BETWEEN %s AND %s
GROUP BY category
ORDER BY spent DESC, category
"""

SUMMARY_SQL = """
SELECT COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) AS income,
       COALESCE(SUM(CASE WHEN amount < 0 THEN -amount ELSE 0 END), 0) AS expenses,
       COALESCE(SUM(amount), 0) AS net,
       COUNT(*) AS transaction_count
FROM transactions
WHERE transaction_date BETWEEN %s AND %s
"""

def _query(sql, start_date, end_date):
    if start_date > end_date:
        raise ValueError('Start date must not be after end date')
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (start_date, end_date))
            columns = [c.name for c in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=columns)

def monthly_report(start_date, end_date):
    df = _query(MONTHLY_SQL, start_date, end_date)
    if not df.empty:
        df['month'] = pd.to_datetime(df['month']).dt.strftime('%Y-%m')
        for col in ('income', 'expenses', 'net'):
            df[col] = df[col].astype(float)
    return df

def category_report(start_date, end_date):
    df = _query(CATEGORY_SQL, start_date, end_date)
    if not df.empty:
        df['spent'] = df['spent'].astype(float)
    return df

def summary_report(start_date, end_date):
    df = _query(SUMMARY_SQL, start_date, end_date)
    row = df.iloc[0]
    return {'income': float(row['income']), 'expenses': float(row['expenses']),
            'net': float(row['net']), 'transaction_count': int(row['transaction_count'])}
