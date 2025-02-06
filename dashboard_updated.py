import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
import scipy as sc
import math as m
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "order_item_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "order_item_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english").order_item_id.sum().sort_values(ascending=False).reset_index()
    sum_order_items_df.rename(columns={
        "product_category_name_english": "product_name",
        "order_item_id" : "quantity"
    }, inplace=True)
    return sum_order_items_df

def create_mean_product_score_df(df):
    mean_product_score_df = df.groupby("product_category_name_english").review_score.mean().sort_values(ascending=False).reset_index()
    mean_product_score_df.rename(columns={
        "product_category_name_english": "product_name",
        "review_score" : "Score"
    }, inplace=True)
    return mean_product_score_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

def haversine(lat1, lng1, lat2, lng2):
    # Jari-jari Bumi (dalam kilometer)
    R = 6371.0
    
    # Konversi derajat ke radian
    lat1, lng1, lat2, lng2 = map(m.radians, [lat1, lng1, lat2, lng2])
    
    # Selisih koordinat
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    # Rumus Haversine
    a = m.sin(dlat / 2)**2 + m.cos(lat1) * m.cos(lat2) * m.sin(dlng / 2)**2
    c = 2 * m.atan2(m.sqrt(a), m.sqrt(1 - a))
    
    # Jarak dalam kilometer
    jarak = R * c
    return jarak

def create_distance_df(df):
    distance_df = df[["order_id","product_category_name_english","customer_id","seller_id","customer_geolocation_lat",
                   "customer_geolocation_lng","seller_geolocation_lat","seller_geolocation_lng"]]
    order_distance = list(map(haversine, distance_df["seller_geolocation_lat"],distance_df["seller_geolocation_lng"],
                              distance_df["customer_geolocation_lat"],distance_df["customer_geolocation_lng"]))
    order_distance = [round(x, 2) for x in order_distance]
    distance_df["order_distance"] = order_distance
    
    return distance_df

def create_delivery_time(df):
    delivery_time = df[["delivery_time"]]
    return delivery_time

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "order_item_value": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

def plot_order(grouped_data,time_period):
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(grouped_data.T, annot=False, cmap="YlGnBu", cbar=True, fmt="d", ax=ax)
    ax.set_title(f"Orders by State ({time_period})")
    ax.set_xlabel(time_period)
    ax.set_ylabel("Customer State")
    
    # Display the plot in Streamlit
    st.pyplot(fig)

def day_(df):
    # Group by day
    grouped_data, time_period =  df.groupby([df['order_purchase_timestamp'].dt.date, 'customer_state']).size().unstack(fill_value=0), "Daily"
    plot_order(grouped_data, time_period)

def week_(df):
    # Group by week
    grouped_data, time_period = df.groupby([pd.Grouper(key='order_purchase_timestamp', freq='W'), 'customer_state']).size().unstack(fill_value=0), "Weekly"
    plot_order(grouped_data, time_period)

def month_(df):
    # Group by month
    grouped_data, time_period = df.groupby([pd.Grouper(key='order_purchase_timestamp', freq='M'), 'customer_state']).size().unstack(fill_value=0), "Monthly"
    plot_order(grouped_data, time_period)
    
def quarter_(df):
    # Group by quarter
    grouped_data, time_period = df.groupby([pd.Grouper(key='order_purchase_timestamp', freq='Q'), 'customer_state']).size().unstack(fill_value=0), "Quarterly"
    plot_order(grouped_data, time_period)

# Define a function to choose the grouping method based on the difference
def group_data_by_date_diff(df, date_diff):
    st.subheader("Count order by date")
    if date_diff < 7:
        day_(df)
        
    elif 7 <= date_diff < 30:
        tab_count1, tab_count2 = st.tabs(["Daily","Weekly"])
        with tab_count1:
            day_(df)
        with tab_count2:
            week_(df)
        
    elif 30 <= date_diff < 90:
        tab_count1, tab_count2,tab_count3 = st.tabs(["Daily","Weekly","Monthly"])
        with tab_count1:
            day_(df)
        with tab_count2:
            week_(df)
        with tab_count3:
            month_(df)

    else:
        tab_count1, tab_count2, tab_count3, tab_count4 = st.tabs(["Daily","Weekly","Monthly","Quarter"])
        with tab_count1:
            day_(df)
        with tab_count2:
            week_(df)
        with tab_count3:
            month_(df)
        with tab_count4:
            quarter_(df)

all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])



min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    
    # # Mengambil start_date & end_date dari date_input
    # start_date, end_date = st.date_input(
    #     label='Time Span',min_value=min_date,
    #     max_value=max_date,
    #     value=[min_date, max_date]
    # )
    st.write("**Choose Filter :**")
    start_date = st.date_input("Start Date", min_value=min_date, 
                               max_value=max_date, value=None)
    end_date = st.date_input("End Date", min_value=start_date, 
                               max_value=max_date, value=None)
    
    try:
        # Jika pengguna tidak memilih tanggal, gunakan default min/max
        if start_date is None:
            start_date = min_date
        if end_date is None:
            end_date = max_date
    
        # Konversi ke datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    
    except Exception as e:
        st.error(f"Terjadi kesalahan dalam filter tanggal: {e}")

    choose_state = st.multiselect("State", all_df["customer_state"].unique())


    if not choose_state:
        choose_state = all_df["customer_state"].unique()

    dummy1 = all_df[(all_df["customer_state"].isin(choose_state))]
    
    choose_city = st.multiselect("City", dummy1["customer_city"].unique())

    # st.write(choose_city is None)

    if not choose_city:
        choose_city = dummy1["customer_city"].unique()

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date)) & 
                (all_df["customer_state"].isin(choose_state)) & 
                (all_df["customer_city"].isin(choose_city))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
mean_product_score_df = create_mean_product_score_df(main_df)
bystate_df = create_bystate_df(main_df)
distance_df = create_distance_df(main_df)
delivery_time = create_delivery_time(main_df)
rfm_df = create_rfm_df(main_df)

st.title('Dashboard of Brazilian E-Commerce Public Dataset by Olist :sparkles:')

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Orders", "Products", "Score", "Demograpics", "RFM"])
 
with tab1:
    st.header("Daily Orders")
    col1, col2 = st.columns(2)
     
    with col1:
        total_orders = daily_orders_df.order_count.sum()
        st.metric("Total orders", value=total_orders)
     
    with col2:
        total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='pt_BR') 
        st.metric("Total Revenue", value=total_revenue)
 
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        daily_orders_df["order_purchase_timestamp"],
        daily_orders_df["order_count"],
        marker='o', 
        linewidth=2,
        color="#90CAF9"
    )
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
     
    st.pyplot(fig)
    
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.histplot(x=delivery_time["delivery_time"],
                 bins=20
                 )
    
    ax.set_title("Delivery Time", loc="center", fontsize=30)
    ax.set_ylabel("Number of Order", fontdict={'fontsize': 20})
    ax.set_xlabel("Days", fontdict={'fontsize': 20})
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)
 
with tab2:
    st.header("Best & Worst Performing Product")
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
     
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
     
    sns.barplot(x="quantity", y="product_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Number of Sales", fontsize=30)
    ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=35)
    ax[0].tick_params(axis='x', labelsize=30)
     
    sns.barplot(x="quantity", y="product_name", data=sum_order_items_df.sort_values(by="quantity", ascending=True).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Number of Sales", fontsize=30)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=35)
    ax[1].tick_params(axis='x', labelsize=30)
    
    st.pyplot(fig)
 
with tab3:
    st.header("Highest & Lowest Product Score") 
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
     
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
     
    sns.barplot(x="Score", y="product_name", data=mean_product_score_df.head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Mean Product Score", fontsize=30)
    ax[0].set_title("Highest Product Score Product", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=35)
    ax[0].tick_params(axis='x', labelsize=30)
     
    sns.barplot(x="Score", y="product_name", data=mean_product_score_df.sort_values(by="Score", ascending=True).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Mean Product Score", fontsize=30)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Lowest Product Score", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=35)
    ax[1].tick_params(axis='x', labelsize=30)
    
    st.pyplot(fig)


with tab4:
    st.header("Demographic")
    st.subheader("Distance")
    
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.histplot(x=distance_df["order_distance"],
                 bins=10
                 )
    
    ax.set_title("Distance from Seller to Customer", loc="center", fontsize=30)
    ax.set_ylabel("Number of Order", fontdict={'fontsize': 20})
    ax.set_xlabel("Distance in kilometers", fontdict={'fontsize': 20})
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

    st.subheader("State")
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3","#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="customer_count", 
        y="customer_state",
        data=bystate_df.sort_values(by="customer_count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by States", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='y', labelsize=20)
    ax.tick_params(axis='x', labelsize=15)
    st.pyplot(fig)

    # tab_demo1, tab_demo

    # Find the min and max date
    min_date = main_df['order_purchase_timestamp'].min()
    max_date = main_df['order_purchase_timestamp'].max()
    
    # Calculate the difference in days between the min and max dates
    date_diff = (max_date - min_date).days

    group_data_by_date_diff(main_df, date_diff)

with tab5:
    st.header("Best Customer Based on RFM Parameters")
     
    col1, col2, col3 = st.columns(3)
     
    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)
     
    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)
     
    with col3:
        avg_frequency = format_currency(rfm_df.monetary.mean(), "BRL", locale='pt_BR') 
        st.metric("Average Monetary", value=avg_frequency)
     
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
    colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
     
    sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("customer_id", fontsize=30)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
    ax[0].tick_params(axis='y', labelsize=30)
    ax[0].tick_params(axis='x', labelrotation=90, labelsize=35)
     
    sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("customer_id", fontsize=30)
    ax[1].set_title("By Frequency", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=30)
    ax[1].tick_params(axis='x', labelrotation=90, labelsize=35)
     
    sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel("customer_id", fontsize=30)
    ax[2].set_title("By Monetary", loc="center", fontsize=50)
    ax[2].tick_params(axis='y', labelsize=30)
    ax[2].tick_params(axis='x', labelrotation=90, labelsize=35)
     
    st.pyplot(fig)

