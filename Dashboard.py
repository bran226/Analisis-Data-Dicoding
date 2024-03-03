import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_monthly_good_review_df(df):
  monthly_good_review_df = df[df["score_indicator"] == "Good"].resample(rule='M', on='order_delivered_customer_date').agg({
  "order_id": "nunique",
  })
  monthly_good_review_df.index = monthly_good_review_df.index.strftime("%Y-%m")
  monthly_good_review_df = monthly_good_review_df.reset_index()
  monthly_good_review_df.rename(columns={
      "order_id": "good_score"
      }, inplace=True)

  monthly_good_review_2017_df = monthly_good_review_df[monthly_good_review_df["order_delivered_customer_date"].str.contains(r'2017')]

  return monthly_good_review_2017_df

def create_monthly_bad_review_df(df):
  monthly_bad_review_df = df[df["score_indicator"] == "Bad"].resample(rule='M', on='order_delivered_customer_date').agg({
    "order_id": "nunique",
    })
  monthly_bad_review_df.index = monthly_bad_review_df.index.strftime("%Y-%m")
  monthly_bad_review_df = monthly_bad_review_df.reset_index()
  monthly_bad_review_df.rename(columns={
      "order_id": "bad_score"
      }, inplace=True)
  
  monthly_bad_review_2017_df = monthly_bad_review_df[monthly_bad_review_df["order_delivered_customer_date"].str.contains(r'2017')]
  
  
  return monthly_bad_review_2017_df

def create_rfm_df(df):
  rfm_df = df.groupby(by="customer_id", as_index=False).agg({
      "order_id": "nunique",
      "payment_value": "sum"
      })
  
  rfm_df.columns = ["customer_id", "frequency", "monetary"]
  
  rfm_df.sort_values(by="monetary")

  return rfm_df

def create_city_df(df):
  city_df = df.groupby(by="customer_city").payment_value.sum().sort_values(ascending=False).reset_index()
  
  return city_df

all_df = pd.read_csv("all_data2.csv")

all_df.sort_values(by="order_delivered_customer_date", inplace=True)
all_df.reset_index(inplace=True)

all_df["order_delivered_customer_date"] = pd.to_datetime(all_df["order_delivered_customer_date"])

min_date = all_df["order_delivered_customer_date"].min()
max_date = all_df["order_delivered_customer_date"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    main_df = all_df[(all_df["order_delivered_customer_date"] >= str(start_date)) & 
                (all_df["order_delivered_customer_date"] <= str(end_date))]

monthly_good_review_2017_df = create_monthly_good_review_df(main_df)
monthly_bad_review_2017_df = create_monthly_bad_review_df(main_df)
rfm_df = create_rfm_df(main_df)
city_df = create_city_df(main_df)

st.header('Khibran Ecommerce Dashboard :sparkles:')

st.subheader('Review Score in 2017')
 
col1, col2 = st.columns(2)
 
with col1:
    total_good_score = monthly_good_review_2017_df.good_score.sum()
    st.metric("Good Score in Total", value=total_good_score)
 
with col2:
    total_bad_score = monthly_bad_review_2017_df.bad_score.sum() 
    st.metric("Bad Score in Total", value=total_bad_score)
 
fig, ax = plt.subplots(figsize=(16, 8))

ax.plot(
    monthly_good_review_2017_df["order_delivered_customer_date"],
    monthly_good_review_2017_df["good_score"],
    marker='o', 
    linewidth=2,
    label='Good',
    color="#90CAF9"
)

ax.plot(
    monthly_bad_review_2017_df["order_delivered_customer_date"],
    monthly_bad_review_2017_df["bad_score"],
    marker='o', 
    linewidth=2,
    label='Bad',
    color="#FF2400"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.legend()
 
st.pyplot(fig)

st.subheader("City with Best and Worst Sales")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="payment_value", y="customer_city", data=city_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("City with the best sales", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)

sns.barplot(x="payment_value", y="customer_city", data=city_df.sort_values(by="payment_value", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("City with the worst sales", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)
 
st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2 = st.columns(2)
 
with col1:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col2:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "R$", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Frequency", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35, rotation=45)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Monetary", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35, rotation=45)
st.pyplot(fig)
 
st.caption('Copyright (c) PT Bran226 2024')
