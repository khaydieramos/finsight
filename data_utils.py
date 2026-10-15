import pandas as pd

REQUIRED_COLUMNS = {"date", "description", "category", "amount"}


def load_transactions(source):
    """Read CSV, validate its schema, and normalize transaction fields.

    Positive amounts represent income; negative amounts represent expenses.
    """
    df = pd.read_csv(source)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    if df["date"].isna().any() or df["amount"].isna().any():
        raise ValueError("Every transaction needs a valid date and numeric amount")
    if df[["description", "category"]].isna().any().any():
        raise ValueError("Descriptions and categories cannot be empty")
    df["category"] = df["category"].astype(str).str.strip()
    df["description"] = df["description"].astype(str).str.strip()
    if (df["category"] == "").any() or (df["description"] == "").any():
        raise ValueError("Descriptions and categories cannot be empty")
    return df.sort_values("date").reset_index(drop=True)


def summarize(df):
    income = float(df.loc[df["amount"] > 0, "amount"].sum())
    expenses = float(-df.loc[df["amount"] < 0, "amount"].sum())
    return {"income": income, "expenses": expenses, "net": income - expenses}


def monthly_cashflow(df):
    if df.empty:
        return pd.DataFrame(columns=["month", "income", "expenses", "net"])
    tmp = df.copy()
    tmp["month"] = tmp["date"].dt.to_period("M").astype(str)
    tmp["income"] = tmp["amount"].clip(lower=0)
    tmp["expenses"] = -tmp["amount"].clip(upper=0)
    result = tmp.groupby("month", as_index=False)[["income", "expenses"]].sum()
    result["net"] = result["income"] - result["expenses"]
    return result


def spending_by_category(df):
    spending = df[df["amount"] < 0].copy()
    spending["spent"] = -spending["amount"]
    return spending.groupby("category", as_index=False)["spent"].sum().sort_values("spent", ascending=False)
