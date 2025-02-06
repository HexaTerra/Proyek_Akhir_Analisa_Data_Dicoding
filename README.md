# Dashboard of Brazilian E-Commerce Public Dataset by Olist

## Overview
The **Brazilian E-Commerce Public Dataset by Olist** is a comprehensive dataset that contains information on orders made on an e-commerce platform in Brazil. This dataset is valuable for data analysis, machine learning applications, and business intelligence insights. The data includes customer details, order items, payments, reviews, and more, allowing for a holistic analysis of the Brazilian e-commerce market.

## Dataset: `olist_order_payments_dataset.csv`

### Description
This dataset is part of the **Brazilian E-Commerce Public Dataset by Olist**, which contains detailed order information from an e-commerce platform in Brazil. The `olist_order_payments_dataset.csv` file specifically includes information on the payment details for each order.

For more details, visit the Kaggle dataset page: [Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

## Setup Environment - Anaconda

```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard.py
```
