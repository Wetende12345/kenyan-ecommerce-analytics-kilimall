import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

st.title("Kilimall Kenyan E-commerce Analytics Dashboard 🇰🇪")

# DB Connection
conn = psycopg2.connect(
    dbname="kilimall_dw",
    user="postgres",
    password="Mamapipi1234#",
    host="localhost",
    port="5432"
)
df_snapshot = pd.read_sql("""
    SELECT d.full_date, AVG(f.price_ksh) AS avg_price, COUNT(*) AS product_count
    FROM fact_product_snapshot f
    JOIN dim_date d ON f.date_sk = d.date_sk
    GROUP BY d.full_date
    ORDER BY d.full_date
""", conn)

df_categories = pd.read_sql("""
    SELECT c.category_name, AVG(f.price_ksh) AS avg_price, COUNT(*) AS products
    FROM fact_product_snapshot f
    JOIN dim_category c ON f.category_sk = c.category_sk
    GROUP BY c.category_name
""", conn)

conn.close()

st.header("Daily Price Trend")
fig_line = px.line(df_snapshot, x='full_date', y='avg_price', title="Average Product Price Over Time (KSh)")
st.plotly_chart(fig_line)

st.header("Product Count per Day")
fig_bar = px.bar(df_snapshot, x='full_date', y='product_count', title="Products Scraped per Day")
st.plotly_chart(fig_bar)

st.header("Average Price by Category")
fig_pie = px.pie(df_categories, values='avg_price', names='category_name', title="Avg Price Distribution")
st.plotly_chart(fig_pie)

st.header("Raw Data Sample")
st.dataframe(pd.read_sql("SELECT * FROM fact_product_snapshot LIMIT 20", psycopg2.connect(dbname="kilimall_dw", user="denwetende", host="localhost")))

st.success("Dashboard updated with live Kilimall data!")
