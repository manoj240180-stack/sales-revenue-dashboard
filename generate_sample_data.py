"""Generate a Superstore-style sample dataset (used if you don't have the Kaggle file)."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 6000

catalog = {
    "Technology": {"Phones": (150, 900), "Accessories": (10, 120), "Copiers": (300, 2500), "Machines": (200, 1800)},
    "Furniture": {"Chairs": (80, 700), "Tables": (150, 1200), "Bookcases": (90, 800), "Furnishings": (15, 150)},
    "Office Supplies": {"Paper": (5, 60), "Binders": (5, 80), "Storage": (15, 200), "Art": (5, 50), "Labels": (3, 25)},
}
regions = {
    "West": ["Los Angeles", "Seattle", "San Francisco"],
    "East": ["New York City", "Philadelphia", "Boston"],
    "Central": ["Chicago", "Houston", "Dallas"],
    "South": ["Atlanta", "Miami", "Charlotte"],
}
segments = ["Consumer", "Corporate", "Home Office"]
ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]

rows = []
dates = pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 4 * 365 // 1, N) % 1096, unit="D")
for i in range(N):
    cat = rng.choice(list(catalog))
    sub = rng.choice(list(catalog[cat]))
    lo, hi = catalog[cat][sub]
    price = round(float(rng.uniform(lo, hi)), 2)
    qty = int(rng.integers(1, 8))
    discount = float(rng.choice([0, 0, 0, 0.1, 0.2, 0.3, 0.5]))
    sales = round(price * qty * (1 - discount), 2)
    margin = rng.normal(0.18, 0.12) - discount * 0.6
    region = rng.choice(list(regions))
    od = dates[i]
    rows.append({
        "Order ID": f"US-{od.year}-{100000 + i}",
        "Order Date": od.date(),
        "Ship Date": (od + pd.Timedelta(days=int(rng.integers(1, 8)))).date(),
        "Ship Mode": rng.choice(ship_modes),
        "Customer ID": f"C-{rng.integers(1000, 1800)}",
        "Segment": rng.choice(segments),
        "Country": "United States",
        "City": rng.choice(regions[region]),
        "Region": region,
        "Category": cat,
        "Sub-Category": sub,
        "Product Name": f"{sub} Model {rng.integers(1, 15)}",
        "Sales": sales,
        "Quantity": qty,
        "Discount": discount,
        "Profit": round(sales * margin, 2),
    })

df = pd.DataFrame(rows)
df.to_csv("data/sample_sales_data.csv", index=False)
print(f"Saved data/sample_sales_data.csv with {len(df)} rows")
