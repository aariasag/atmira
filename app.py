import pandas as pd
import streamlit as st
import os
import plotly.express as px
import datetime
from streamlit_option_menu import option_menu

#Set local path
path = os.path.abspath(os.getcwd())

#Read excel
@st.cache(suppress_st_warning=True)
def data_read():
    df = pd.read_csv(path + '/data/parte1.csv')
    df['date']=pd.to_datetime(df['date'], format='%Y-%m-%d').dt.date
    return df

df = data_read()


#### MENU DEL DASHBOARD ####
st.sidebar.markdown("# Atmira Dashboard")

start_date = st.sidebar.date_input('Start date', value=datetime.date(2017,1,1), min_value=datetime.date(2017,1,1), max_value=datetime.date(2018,12,30))
end_date = st.sidebar.date_input('End date', value=datetime.date(2018,12,30), min_value = datetime.date(2017,1,1), max_value=datetime.date(2018,12,30))

category_list = list(df['analytic_category'].unique())
selected_category = st.sidebar.multiselect('Choose a category', category_list,category_list[:])

#### VENTAS POR CATEGORIA EN UN PERIODO ###
latest_data = df[(df['date']<=end_date) & (df['date']>=start_date)]

grouped_data = (
    latest_data.dropna(subset=['analytic_category']).groupby('analytic_category')['sales','benefit'].sum()
               .sort_values('sales').reset_index()
)

filtered_data = grouped_data[grouped_data['analytic_category'].isin(selected_category)]

fig  = px.bar(filtered_data.iloc[:],
              x=["sales","benefit"],
              y="analytic_category",
              barmode = 'group',
              orientation='h')

st.write("""## Sales by Category""")
st.plotly_chart(fig)

#### SCATTER PLOT DEL PRECIO DE UN PRODUCTO Y SU COSTE BASE PARA LA DETECCIÓN DE ANOMALÍAS ###

grouped_data = (
    latest_data.dropna(subset=['name', 'base_cost', 'price']).groupby(['analytic_category', 'name'])[
        'price', 'base_cost','benefit'].mean().reset_index()

)

filtered_data = grouped_data[grouped_data['analytic_category'].isin(selected_category)]

#Eliminamos los productos con precio o coste base cero
filtered_data = filtered_data[(filtered_data.price>0) & (filtered_data.base_cost >0) & (filtered_data.benefit>0)]

#Usamos escala logarítmica en x e y para una mejor representación
fig = px.scatter(filtered_data,
           x='price',
           y='base_cost',
           size = 'benefit',
           color = 'analytic_category',
          # size_max=60,
           log_x = True,
           log_y = True,
           hover_name='name')

fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))

st.write("""## Mean Base Cost vs Mean Product Price""")
st.write("""Bubble size is proportional to mean product benefit""")
st.plotly_chart(fig)

#### EVOLUCIÓN TEMPORAL DE LAS VENTAS



filtered_data = latest_data[latest_data['analytic_category'].isin(selected_category)]

selected_data = (
    filtered_data.dropna(subset=['date', 'sales']).groupby(['date'])['sales'].sum().reset_index()

)


st.write("""## Sales evolution""")
st.write("""We observed 2 peaks corresponding to Black Fridays 24/11/2017 and 23/11/2018""")
fig = px.line(selected_data, x='date', y='sales')

fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))

st.plotly_chart(fig)

#### EVOLUCIÓN TEMPORAL DE LAS VENTAS POR DÍA Y HORA

selected_data = (
    latest_data.dropna(subset=['date', 'hour', 'sales']).groupby(['date', 'hour'])['sales'].sum().reset_index()

)
selected_data2D = selected_data.pivot(index='date',values='sales',columns='hour')

st.write("""## Sales evolution per date and hour""")

fig=px.imshow(selected_data2D)
st.plotly_chart(fig)

### TOP 10 MOST SOLD PRODUCTS

start_date = datetime.date(2018, 11, 23)
end_date = datetime.date(2018, 11, 23)

latest_data = df[(df['date'] <= end_date) & (df['date'] >= start_date)]
selected_data = (
    latest_data.dropna(subset=['name']).groupby(['name'])['qty_ordered'].sum().reset_index()

)

st.write("""## TOP 10 MOST SOLD PRODUCTS""")

most_sold_products = selected_data.sort_values(by='qty_ordered',ascending=False).head(10).reset_index()
most_sold_products = most_sold_products[['name','qty_ordered']]
most_sold_products['qty_ordered'] = most_sold_products['qty_ordered'].astype(int)

st.table(most_sold_products)