"""Sales & Revenue Analysis Dashboard (Streamlit + Plotly)."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sales & Revenue Dashboard", page_icon="📊", layout="wide")

DATA_DIR = Path(__file__).parent / "data"
CANDIDATES = ["superstore.csv", "Sample - Superstore.csv", "sample_sales_data.csv"]


@st.cache_data
def load_data(uploaded=None) -> tuple[pd.DataFrame, str]:
    if uploaded is not None:
        try:
            df, name = pd.read_csv(uploaded), uploaded.name
        except UnicodeDecodeError:
            uploaded.seek(0)
            df, name = pd.read_csv(uploaded, encoding="latin-1"), uploaded.name
    else:
        path = next((DATA_DIR / c for c in CANDIDATES if (DATA_DIR / c).exists()), None)
        if path is None:
            st.error("No dataset found. Put a CSV in the data/ folder or run generate_sample_data.py")
            st.stop()
        try:
            df = pd.read_csv(path)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="latin-1")
        name = path.name

    df.columns = [c.strip() for c in df.columns]
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df = df.dropna(subset=["Order Date", "Sales"]).drop_duplicates()
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    return df, name


# ---------- Sidebar ----------
st.sidebar.header("Filters")
upload = st.sidebar.file_uploader("Upload your own sales CSV (optional)", type="csv")
df, source = load_data(upload)
st.sidebar.caption(f"Data source: {source}")

years = st.sidebar.multiselect("Year", sorted(df["Year"].unique()), default=sorted(df["Year"].unique()))
regions = st.sidebar.multiselect("Region", sorted(df["Region"].unique()), default=sorted(df["Region"].unique()))
cats = st.sidebar.multiselect("Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))

f = df[df["Year"].isin(years) & df["Region"].isin(regions) & df["Category"].isin(cats)]
if f.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ---------- KPIs ----------
st.title("📊 Sales & Revenue Analysis Dashboard")
total_sales, total_profit = f["Sales"].sum(), f["Profit"].sum()
orders = f["Order ID"].nunique()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Sales", f"${total_sales:,.0f}")
c2.metric("Total Profit", f"${total_profit:,.0f}")
c3.metric("Profit Margin", f"{total_profit / total_sales:.1%}")
c4.metric("Orders", f"{orders:,}")
c5.metric("Avg Order Value", f"${total_sales / orders:,.2f}")

st.divider()

# ---------- Revenue trend ----------
monthly = f.groupby("Month", as_index=False)[["Sales", "Profit"]].sum()
fig = px.line(monthly, x="Month", y=["Sales", "Profit"], markers=True, title="Monthly Revenue & Profit Trend")
fig.update_layout(legend_title_text="", yaxis_title="Amount ($)")
st.plotly_chart(fig, width="stretch")

# ---------- Category / Region ----------
left, right = st.columns(2)
cat_sales = f.groupby("Category", as_index=False)["Sales"].sum()
left.plotly_chart(px.pie(cat_sales, names="Category", values="Sales", hole=0.45, title="Sales by Category"),
                  width="stretch")
reg = f.groupby("Region", as_index=False)[["Sales", "Profit"]].sum()
right.plotly_chart(px.bar(reg, x="Region", y=["Sales", "Profit"], barmode="group", title="Sales & Profit by Region"),
                   width="stretch")

# ---------- Top products ----------
left, right = st.columns(2)
top = f.groupby("Product Name", as_index=False)["Sales"].sum().nlargest(10, "Sales").sort_values("Sales")
left.plotly_chart(px.bar(top, x="Sales", y="Product Name", orientation="h", title="Top 10 Products by Sales"),
                  width="stretch")
sub = f.groupby("Sub-Category", as_index=False)["Profit"].sum().sort_values("Profit")
sub["Result"] = sub["Profit"].apply(lambda x: "Profit" if x >= 0 else "Loss")
right.plotly_chart(
    px.bar(sub, x="Profit", y="Sub-Category", orientation="h", color="Result",
           color_discrete_map={"Profit": "#2e86de", "Loss": "#e74c3c"}, title="Profit by Sub-Category"),
    width="stretch")

# ---------- Discount impact ----------
disc = f.groupby("Discount", as_index=False)["Profit"].mean()
st.plotly_chart(px.bar(disc, x="Discount", y="Profit", title="Average Profit per Order Line by Discount Level"),
                width="stretch")

# ---------- Data ----------
with st.expander("View filtered data"):
    st.dataframe(f.drop(columns=["Month"]), width="stretch")
    st.download_button("Download filtered CSV", f.to_csv(index=False), "filtered_sales.csv", "text/csv")
