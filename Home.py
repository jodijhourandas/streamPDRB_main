# streamlit_app.py

import streamlit as st
from streamlit_gsheets import GSheetsConnection
from st_aggrid import AgGrid
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from st_aggrid.grid_options_builder import GridOptionsBuilder

# Page configuration

st.set_page_config(
    page_title="Stream PDRB",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

# Try elements 

# Function
def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} Triliun'
        return f'{round(num / 1000000, 1)} Triliun'
    return f'{num // 1000} Miliar'

def df_style(val):
    return "font-weight: bold"

def sog(df_diff, df_growth):
    pdrb = df_diff.PDRB
    growth = df_growth.PDRB
    res = df_diff.div(pdrb,axis = 0).mul(growth,axis = 0).round(2)
    return res



def loading_first(kode,_conn):
    
    s_adhb = f'{kode}_adhb' 
    s_adhk = f'{kode}_adhk'
    df_adhb = pd.DataFrame(_conn.read(worksheet=s_adhb,rows=18))
    df_adhk = pd.DataFrame(_conn.read(worksheet=s_adhk,rows=18))
    df_adhb.set_index("Komponen", inplace=True)
    df_adhk.set_index("Komponen", inplace=True)

    df_adhb_q  = df_adhb.filter(regex = "Q").round(2)
    df_adhk_q  = df_adhk.filter(regex = "Q").round(2)
    df_adhb_y  = df_adhb.drop(df_adhb.filter(regex='Q').columns,axis=1)
    df_adhk_y  = df_adhk.drop(df_adhk.filter(regex='Q').columns,axis=1)
    
    impli_q = df_adhb_q.div(df_adhk_q).mul(100)
    impli_y = df_adhb_y.div(df_adhk_y).mul(100)

    qq = df_adhk_q.T.pct_change(periods=1).mul(100)
    yy = df_adhk_q.T.pct_change(periods=4).mul(100)
    qq_y = df_adhk_y.T.pct_change(periods=1).mul(100)
    yy_y = df_adhk_y.T.pct_change(periods=4).mul(100)
    
    qq_diff = sog(df_adhk_q.T.diff(periods=1),qq)
    yy_diff =  sog(df_adhk_q.T.diff(periods=4),yy)
    qq_y_diff =  sog(df_adhk_y.T.diff(periods=1),qq_y)
    yy_y_diff =  sog(df_adhk_y.T.diff(periods=4),yy_y)

    imp_qq = impli_q.T.pct_change(periods=1).mul(100)
    imp_yy = impli_q.T.pct_change(periods=4).mul(100)
    imp_qq_y = impli_y.T.pct_change(periods=1).mul(100)
    imp_yy_y = impli_y.T.pct_change(periods=4).mul(100)
    
    cc = df_adhk_q.T
    cc['year'] = cc.index.str[:4]
    cc = cc.groupby('year').cumsum().pct_change(periods=4).mul(100)

    imp_cc = impli_q.T
    imp_cc['year'] = imp_cc.index.str[:4]
    imp_cc = imp_cc.groupby('year').cumsum().pct_change(periods=4).mul(100)

    cc_diff = df_adhk_q.T
    cc_diff['year'] = cc_diff.index.str[:4]
    cc_diff = sog(cc_diff.groupby('year').cumsum().diff(periods=4).round(2),cc)
    
    if f'df_adhb_q_{kode}' not in st.session_state:
        st.session_state[f'df_adhb_q_{kode}'] = df_adhb_q
    if f'df_adhk_q_{kode}' not in st.session_state:
        st.session_state[f'df_adhk_q_{kode}'] = df_adhk_q
    if f'df_adhb_y_{kode}' not in st.session_state:
        st.session_state[f'df_adhb_y_{kode}'] = df_adhb_y
    if f'df_adhk_y_{kode}' not in st.session_state:
        st.session_state[f'df_adhk_y_{kode}'] = df_adhk_y
    if f'qq_{kode}' not in st.session_state:
        st.session_state[f'qq_{kode}'] = qq
    if f'yy_{kode}' not in st.session_state:
        st.session_state[f'yy_{kode}'] = yy
    if f'qq_y_{kode}' not in st.session_state:
        st.session_state[f'qq_y_{kode}'] = qq_y
    if f'yy_y_{kode}' not in st.session_state:
        st.session_state[f'yy_y_{kode}'] = yy_y
    if f'cc_{kode}' not in st.session_state:
        st.session_state[f'cc_{kode}'] = cc
    if f'cc_diff_{kode}' not in st.session_state:
        st.session_state[f'cc_diff_{kode}'] = cc_diff  
    if f'impli_q_{kode}' not in st.session_state:
        st.session_state[f'impli_q_{kode}'] = impli_q   
    if f'impli_y_{kode}' not in st.session_state:
        st.session_state[f'impli_y_{kode}'] = impli_y  
    if f'imp_qq_{kode}' not in st.session_state:
        st.session_state[f'imp_qq_{kode}'] = imp_qq
    if f'imp_yy_{kode}' not in st.session_state:
        st.session_state[f'imp_yy_{kode}'] = imp_yy
    if f'imp_qq_y_{kode}' not in st.session_state:
        st.session_state[f'imp_qq_y_{kode}'] = imp_qq_y
    if f'imp_yy_y_{kode}' not in st.session_state:
        st.session_state[f'imp_yy_y_{kode}'] = imp_yy_y
    if f'imp_cc_{kode}' not in st.session_state:
        st.session_state[f'imp_cc_{kode}'] = imp_cc  
    if f'qq_diff_{kode}' not in st.session_state:
        st.session_state[f'qq_diff_{kode}'] = qq_diff
    if f'yy_diff_{kode}' not in st.session_state:
        st.session_state[f'yy_diff_{kode}'] = yy_diff
    if f'qq_y_diff_{kode}' not in st.session_state:
        st.session_state[f'qq_y_diff_{kode}'] = qq_y_diff
    if f'yy_y_diff_{kode}' not in st.session_state:
        st.session_state[f'yy_y_diff_{kode}'] = yy_y_diff
# Load data
kodes = ['6100','6101','6102','6103','6104','6105','6106',
         '6107','6108','6109','6110','6111','6112','6171','6172']

kode = st.selectbox('Pilih kabupaten', kodes, index=0)
st.session_state["kode"] = kode
conn = st.connection("gsheets", type=GSheetsConnection)

if f'df_adhb_q_{kode}' not in st.session_state:
    with st.spinner(text="Loading data..."):
        for kode in kodes:
            loading_first(kode,conn)

# Komponen awal
# Define your custom CSS
##st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.subheader('PDRB Summary : ', divider='rainbow')
year_list = st.session_state[f'df_adhb_q_{kode}'].columns.to_list()
selected_year = st.selectbox('Select a year', reversed(year_list), index=0)
idx = st.session_state[f'df_adhb_q_{kode}'].columns.get_loc(selected_year)
#st.markdown(f'#### PDRB- {selected_year} ')

col1,col2,col3,col4,col5 = st.columns(5, gap="small")

with col1:
    value = st.session_state[f'df_adhb_q_{kode}'].iloc[16,idx].round(2)
    prev = st.session_state[f'df_adhb_q_{kode}'].iloc[16,idx-1] .round(2)
    delta =  value - prev
    st.metric(label="Total PDRB ADHB", value= format_number(value), delta= format_number(delta))
with col2:
    value = st.session_state[f'df_adhk_q_{kode}'].iloc[16,idx].round(2)
    prev = st.session_state[f'df_adhk_q_{kode}'].iloc[16,idx-1].round(2) 
    delta = value - prev
    st.metric(label="Total PDRB ADHK", value= format_number(value), delta= format_number(delta))
with col3:
    value = st.session_state[f'yy_{kode}'].iloc[st.session_state[f'yy_{kode}'].index.get_loc(selected_year), st.session_state[f'yy_{kode}'].columns.get_loc("PDRB")].round(2) 
    st.metric(label="Y-ON-Y", value= f'{value} %')
with col4:
    value = st.session_state[f'qq_{kode}'].iloc[st.session_state[f'qq_{kode}'].index.get_loc(selected_year),st.session_state[f'qq_{kode}'].columns.get_loc("PDRB")].round(2) 
    st.metric(label="Q-ON-Q", value= f'{value} %')
with col5:    
    value = st.session_state[f'cc_{kode}'].iloc[st.session_state[f'cc_{kode}'].index.get_loc(selected_year),st.session_state[f'cc_{kode}'].columns.get_loc("PDRB")].round(2) 
    st.metric(label="C-ON-C", value= f'{value} %')

#Treemap


dropped = ['1. Konsumsi Rumah Tangga' ,'4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)',"PDRB"]

root = ['1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga',
        '2. Konsumsi Lembaga Nonprofit yang Melayani Rumah Tangga','3. Konsumsi Pemerintah', '4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)',
         '4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)','5. Perubahan Inventori','6. Ekspor','7. Impor']

df_tree = st.session_state[f'df_adhb_q_{kode}'].drop(dropped)
df_tree["root"] = root
fig = px.treemap(df_tree.reset_index(), path = ["root","Komponen"], values=selected_year)
st.plotly_chart(fig, use_container_width=True)

main_list = ['    1.a. Makanan, Minuman, dan Rokok',
       '    1.b. Pakaian dan Alas Kaki',
       '    1.c. Perumahan, Perkakas, Perlengkapan dan Penyelenggaraan Rumah Tangga',
       '    1.d. Kesehatan dan Pendidikan',
       '    1.e. Transportasi, Komunikasi, Rekreasi, dan Budaya',
       '    1.f. Hotel dan Restoran', '    1.g. Lainnya', '    4.a. Bangunan',
       '    4.b. Non-Bangunan',"PDRB"]

def plotSOG(dataset,title):
    df_bar = dataset.T.drop(dropped)
    df_bar["root"] = root
    fig = px.bar(df_bar.reset_index(), x="root", y=selected_year, color="Komponen", title=title)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

col1,col2,col3 = st.columns(3)

plotSOG(st.session_state[f'qq_diff_{kode}'],"Source of growth (Y-on-Y)")
##with col2:
   ## plotSOG(st.session_state.yy_diff,"Source of growth (Q-to-Q)")
##with col3:
    ##plotSOG(st.session_state.cc_diff,"Source of growth (C-to-C)") 
#Grafik growth

st.subheader('Line chart growth : ', divider='rainbow')
col1, col2, col3 ,col4 = st.columns(4)

with col1:
    var_selected = st.selectbox( "Komponen :", st.session_state[f'qq_{kode}'].columns , index = 16 )
with col2:
    mode = st.selectbox("Mode : ", ["Q-to-Q", "Y-on-Y","C-to-C"],index=0)
with col3:
    frequ = st.radio("Frequency : ", ["quarterly", "yearly"],index=0, horizontal=True)    

def plotGrowth(dataset,var_selected =var_selected):
    fig = px.line(dataset.reset_index(), x="index", y=var_selected, markers=True)
    st.plotly_chart(fig, use_container_width=True)

if frequ == "quarterly":
    if mode == "Q-to-Q" :
        plotGrowth(st.session_state[f'qq_{kode}'])
    elif mode == "Y-on-Y" :
        plotGrowth(st.session_state[f'yy_{kode}'])
    elif mode == "C-to-C" :
        plotGrowth(st.session_state[f'cc_{kode}'])
else:
    if mode == "Q-to-Q" :
        plotGrowth(st.session_state[f'qq_y_{kode}'])
    elif mode == "Y-on-Y" :
        plotGrowth(st.session_state[f'qq_y_{kode}'])
    elif mode == "C-to-C" :
        plotGrowth(st.session_state[f'qq_y_{kode}'])




