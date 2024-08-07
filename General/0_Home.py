# streamlit_app.py

import streamlit as st
from st_aggrid import AgGrid
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_elements import elements, mui, html, nivo, sync, event
from streamlit import session_state as state
from types import SimpleNamespace
from General.dashboard import Dashboard, Editor, Card, DataGrid, Radar, Pie, Player
import json
# Page configuration

st.set_page_config(
    page_title="Stream PDRB",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

# Elements

real_cols = ["1. Konsumsi Rumah Tangga","    1.a. Makanan, Minuman, dan Rokok","    1.b. Pakaian dan Alas Kaki","    1.c. Perumahan, Perkakas, Perlengkapan dan Penyelenggaraan Rumah Tangga", 
"    1.d. Kesehatan dan Pendidikan","    1.e. Transportasi, Komunikasi, Rekreasi, dan Budaya","    1.f. Hotel dan Restoran","    1.g. Lainnya"
,"2. Konsumsi Lembaga Nonprofit yang Melayani Rumah Tangga","3. Konsumsi Pemerintah",
"4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)","    4.a. Bangunan","    4.b. Non-Bangunan",
"5. Perubahan Inventori","6. Ekspor","7. Impor","PDRB" 
]
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



def loading_first(kode,df_adhb,df_adhk):
    
    s_adhb = f'{kode}_adhb' 
    s_adhk = f'{kode}_adhk'
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
    
    if f'df_adhb_{kode}' not in st.session_state:
        st.session_state[f'df_adhb_{kode}'] = df_adhb
    if f'df_adhk_{kode}' not in st.session_state:
        st.session_state[f'df_adhk_{kode}'] = df_adhk
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
kabs = ['6101','6102','6103','6104','6105','6106',
         '6107','6108','6109','6110','6111','6112','6171','6172']

kode = st.selectbox('Pilih kabupaten', kodes, index=0)
st.session_state["kode"] = kode


if f'df_adhb_q_{kode}' not in st.session_state:
    conn = st.connection('mysql', type='sql')
    df = conn.query('SELECT * from pdrb;')
    adhk = df[df.tipe == "adhk"]
    adhb = df[df.tipe == "adhb"]
    for kode in kodes:
        adhk_temp = adhk[adhk.kode == int(kode)].drop(["kode","tipe"],axis = 1).set_index("periode")
        adhb_temp = adhb[adhb.kode == int(kode)].drop(["kode","tipe"],axis = 1).set_index("periode")
        adhk_temp.columns = real_cols
        adhb_temp.columns = real_cols
        adhk_temp = adhk_temp.T.reset_index().rename(columns = {"index":"Komponen"})
        adhb_temp = adhb_temp.T.reset_index().rename(columns = {"index":"Komponen"})
        loading_first(kode,adhb_temp,adhk_temp)

# Komponen awal
# Define your custom CSS
##st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.subheader('PDRB Summary : ', divider='rainbow')
year_list = st.session_state[f'df_adhb_q_{kode}'].columns.to_list()
selected_year = st.selectbox('Select a year', reversed(year_list), index=0)
idx = st.session_state[f'df_adhb_q_{kode}'].columns.get_loc(selected_year)
#st.markdown(f'#### PDRB- {selected_year} ')
new_json = dict()



def getLineJson(kode,tipe = "df_adhb_q_"):
    dat = st.session_state[f'{tipe}{kode}'].iloc[16,].T.reset_index().dropna()
    dat.columns = ["id","value"]
    dat =json.loads(dat.to_json(orient="records"))
    return dat

def getLineJsonGrow(kode,tipe = "yy_"):
    dat = st.session_state[f'{tipe}{kode}'].loc[:, "PDRB"].reset_index().dropna()
    dat.columns = ["id","value"]
    dat = json.loads(dat.to_json(orient="records"))
    return dat

def getElevElements(name,title,value,dat):
    with elements(name): 
        mui.Typography(title,variant = "overline",align = "center")
        with mui.Card( sx={"display": "flex", "flexDirection": "column", "borderRadius": 1, "overflow": "hidden"}, elevation=7):
            
            
            with mui.CardContent(sx={"flex": 50}):
                
                DATA = dat
                with mui.Box(sx={"height": 20}):
                    nivo.Bar(data = dat,enableLabel = False,enableGridX = False , enableGridY = False,
                             isInteractive = False)
            mui.Typography(value,variant = "h5",align = "center",fontFamily= 'Segoe UI')    


col1,col2,col3,col4,col5 = st.columns(5, gap="small")

with col1:
    value = st.session_state[f'df_adhb_q_{kode}'].iloc[16,idx].round(2)
    #st.metric(label="Total PDRB ADHB", value= format_number(value), delta= format_number(delta))
    dat = getLineJson(kode)
    getElevElements("adhb","PDRB ADHB",format_number(value),dat)
    
with col2:
    value = st.session_state[f'df_adhk_q_{kode}'].iloc[16,idx].round(2)
    dat = getLineJson(kode,"df_adhk_q_")
    getElevElements("adhk","PDRB ADHK",format_number(value),dat)
with col3:
    value = st.session_state[f'yy_{kode}'].iloc[st.session_state[f'yy_{kode}'].index.get_loc(selected_year), st.session_state[f'yy_{kode}'].columns.get_loc("PDRB")].round(2) 
    dat = getLineJsonGrow(kode,"yy_")
    getElevElements("yy","Y-ON-Y",f'{value} %',dat)
with col4:
    value = st.session_state[f'qq_{kode}'].iloc[st.session_state[f'qq_{kode}'].index.get_loc(selected_year),st.session_state[f'qq_{kode}'].columns.get_loc("PDRB")].round(2) 
    dat = getLineJsonGrow(kode,"qq_")
    getElevElements("qq","Q-ON-Q",f'{value} %',dat)

with col5:    
    value = st.session_state[f'cc_{kode}'].iloc[st.session_state[f'cc_{kode}'].index.get_loc(selected_year),st.session_state[f'cc_{kode}'].columns.get_loc("PDRB")].round(2) 
    dat = getLineJsonGrow(kode,"cc_")
    getElevElements("cc","C-ON-C",f'{value} %',dat)

#Treemap


dropped =  ["    1.a. Makanan, Minuman, dan Rokok","    1.b. Pakaian dan Alas Kaki","    1.c. Perumahan, Perkakas, Perlengkapan dan Penyelenggaraan Rumah Tangga", 
"    1.d. Kesehatan dan Pendidikan","    1.e. Transportasi, Komunikasi, Rekreasi, dan Budaya","    1.f. Hotel dan Restoran","    1.g. Lainnya"
,"    4.a. Bangunan","    4.b. Non-Bangunan","PDRB"
]
root = ['1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga','1. Konsumsi Rumah Tangga',
        '2. Konsumsi Lembaga Nonprofit yang Melayani Rumah Tangga','3. Konsumsi Pemerintah', '4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)',
         '4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)','5. Perubahan Inventori','6. Ekspor','7. Impor']
dropped2 = ['1. Konsumsi Rumah Tangga' ,'4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)',"PDRB"]
dropped_pkrt = ["    1.a. Makanan, Minuman, dan Rokok","    1.b. Pakaian dan Alas Kaki","    1.c. Perumahan, Perkakas, Perlengkapan dan Penyelenggaraan Rumah Tangga", 
"    1.d. Kesehatan dan Pendidikan","    1.e. Transportasi, Komunikasi, Rekreasi, dan Budaya","    1.f. Hotel dan Restoran","    1.g. Lainnya"]

## First Pie

colpie1,colpie2,colpie3 = st.columns(3)
df_tree = st.session_state[f'df_adhb_q_{kode}'].drop(dropped,axis = 0)
df_tree["id"] = ["PKRT","LNPRT","KP","PMTB","Inventori","Ekspor","Impor"]
df_tree["color"] = ["hsl(169, 70%, 50%)","hsl(200, 70%, 50%)","hsl(290, 70%, 50%)","hsl(31, 70%, 50%)","hsl(14, 70%, 50%)","hsl(34, 70%, 50%)","hsl(53, 70%, 50%)"]
df_tree["label"] = df_tree.index
df_tree = df_tree[["id","label",selected_year,"color"]]
df_tree.columns = ["id","label","value","color"]
df_tree.value = (100* df_tree.value/df_tree.value.sum() ).round(2)
data_pie =  json.loads(df_tree.to_json(orient="records"))


df_pkrt = st.session_state[f'df_adhb_q_{kode}'].iloc[1:8,]
df_pkrt["id"] = ["1A","1B","1C","1D","1E","1F","1G"]
df_pkrt["color"] = ["hsl(169, 70%, 50%)","hsl(200, 70%, 50%)","hsl(290, 70%, 50%)","hsl(31, 70%, 50%)","hsl(14, 70%, 50%)","hsl(34, 70%, 50%)","hsl(34, 70%, 50%)"]
df_pkrt["label"] = df_pkrt.index
df_pkrt = df_pkrt[["id","label",selected_year,"color"]]
df_pkrt.columns = ["id","label","value","color"]
df_pkrt.value = (100* df_pkrt.value/df_pkrt.value.sum() ).round(2)
data_pie_2 =  json.loads(df_pkrt.to_json(orient="records"))

df_pmtb = st.session_state[f'df_adhb_q_{kode}'].iloc[11:13,]

df_pmtb["id"] = ["4A","4B"]
df_pmtb["color"] = ["hsl(169, 70%, 50%)","hsl(200, 70%, 50%)"]
df_pmtb["label"] = df_pmtb.index
df_pmtb = df_pmtb[["id","label",selected_year,"color"]]
df_pmtb.columns = ["id","label","value","color"]
df_pmtb.value = (100* df_pmtb.value/df_pmtb.value.sum() ).round(2)
data_pie_3 =  json.loads(df_pmtb.to_json(orient="records"))


with colpie1:
    with elements("demo_7"):
        mui.Typography("Share Komponen PDRB",variant = "overline",align = "center")
        with mui.Card( sx={"display": "flex", "flexDirection": "column", "borderRadius": 1, "overflow": "hidden"}, elevation=7):
           
                with mui.Box(sx={"height": 300}):
                    nivo.Pie(
                        data=data_pie,
                        margin={ "top": 50, "right": 50, "bottom": 50, "left": 50 },
                        innerRadius=0.5,
                        padAngle=0.7,
                        cornerRadius=3,
                        activeOuterRadiusOffset=8,
                        enableArcLabels = False,
                        arcLinkLabelsThickness  = 0,
                        arcLinkLabelsOffset = -3,
                        borderWidth=1,
                        borderColor={
                            "from": "color",
                            "modifiers": [
                                [
                                    "darker",
                                    0.2,
                                ]
                            ]
                        },
                        arcLinkLabelsStraightLength = 0 ,
                        arcLinkLabelsColor={ "from": "color" },
                        defs=[
                            {
                                "id": "dots",
                                "type": "patternDots",
                                "background": "inherit",
                                "color": "rgba(255, 255, 255, 0.3)",
                                "size": 4,
                                "padding": 1,
                                "stagger": True
                            },
                            {
                                "id": "lines",
                                "type": "patternLines",
                                "background": "inherit",
                                "color": "rgba(255, 255, 255, 0.3)",
                                "rotation": -45,
                                "lineWidth": 6,
                                "spacing": 10
                            }
                        ],
                        fill=[
                            { "match": { "id": "PKRT" }, "id": "dots" },
                            { "match": { "id": "LNPRT" }, "id": "dots" },
                            { "match": { "id": "KP" }, "id": "dots" },
                            { "match": { "id": "PMTB" }, "id": "dots" },
                            { "match": { "id": "Inventori" }, "id": "lines" },
                            { "match": { "id": "Ekspor" }, "id": "lines" },
                            { "match": { "id": "Impor" }, "id": "lines" },
                            { "match": { "id": "javascript" }, "id": "lines" }
                        ]
                    )
with colpie2:
    with elements("pie_2"):
        mui.Typography("Share Komponen PKRT",variant = "overline",align = "center")
        with mui.Card( sx={"display": "flex", "flexDirection": "column", "borderRadius": 1, "overflow": "hidden"}, elevation=7):
           
                with mui.Box(sx={"height": 300}):
                    nivo.Pie(
                        data=data_pie_2,
                        margin={ "top": 50, "right": 50, "bottom": 50, "left": 50 },
                        innerRadius=0.5,
                        padAngle=0.7,
                        cornerRadius=3,
                        activeOuterRadiusOffset=8,
                        enableArcLabels = False,
                        arcLinkLabelsThickness  = 0,
                        arcLinkLabelsOffset = -3,
                        borderWidth=1,
                        borderColor={
                            "from": "color",
                            "modifiers": [
                                [
                                    "darker",
                                    0.2,
                                ]
                            ]
                        },
                        arcLinkLabelsStraightLength = 0 ,
                        arcLinkLabelsColor={ "from": "color" },
                        defs=[
                            {
                                "id": "dots",
                                "type": "patternDots",
                                "background": "inherit",
                                "color": "rgba(255, 255, 255, 0.3)",
                                "size": 4,
                                "padding": 1,
                                "stagger": True
                            },
                            {
                                "id": "lines",
                                "type": "patternLines",
                                "background": "inherit",
                                "color": "rgba(255, 255, 255, 0.3)",
                                "rotation": -45,
                                "lineWidth": 6,
                                "spacing": 10
                            }
                        ],
                        fill=[
                            { "match": { "id": "1A" }, "id": "dots" },
                            { "match": { "id": "1B" }, "id": "dots" },
                            { "match": { "id": "1C" }, "id": "dots" },
                            { "match": { "id": "1D" }, "id": "dots" },
                            { "match": { "id": "1E" }, "id": "lines" },
                            { "match": { "id": "1F" }, "id": "lines" },
                            { "match": { "id": "1G" }, "id": "lines" },
                            { "match": { "id": "javascript" }, "id": "lines" }
                        ]
                    )
with colpie3:
    with elements("pie_3"):
        mui.Typography("Share Komponen PMTB",variant = "overline",align = "center")
        with mui.Card( sx={"display": "flex", "flexDirection": "column", "borderRadius": 1, "overflow": "hidden"}, elevation=7):
           
                with mui.Box(sx={"height": 300}):
                    nivo.Pie(
                        data=data_pie_3,
                        tooltip = "label",
                        margin={ "top": 50, "right": 50, "bottom": 50, "left": 50 },
                        innerRadius=0.5,
                        padAngle=0.7,
                        cornerRadius=3,
                        activeOuterRadiusOffset=8,
                        enableArcLabels = False,
                        arcLinkLabelsThickness  = 0,
                        arcLinkLabelsOffset = -3,
                        borderWidth=1,
                        borderColor={
                            "from": "color",
                            "modifiers": [
                                [
                                    "darker",
                                    0.2,
                                ]
                            ]
                        },
                        arcLinkLabelsStraightLength = 0 ,
                        arcLinkLabelsColor={ "from": "color" },
                        defs=[
                            {
                                "id": "dots",
                                "type": "patternDots",
                                "background": "inherit",
                                "color": "rgba(255, 255, 255, 0.3)",
                                "size": 4,
                                "padding": 1,
                                "stagger": True
                            },
                            {
                                "id": "lines",
                                "type": "patternLines",
                                "background": "inherit",
                                "color": "rgba(255, 255, 255, 0.3)",
                                "rotation": -45,
                                "lineWidth": 6,
                                "spacing": 10
                            }
                        ],
                        fill=[
                            { "match": { "id": "4A" }, "id": "dots" },
                            { "match": { "id": "4B" }, "id": "dots" },
                            { "match": { "id": "javascript" }, "id": "lines" }
                        ]
                    )




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
    fig = px.line(dataset.reset_index(), x="periode", y=var_selected, markers=True)
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




# Bump chart

st.markdown("**Bump Chart Ranking Komponen PDRB :**")
komp_selected = st.selectbox("Komponen :",real_cols,index=16 ,key="komponen_bump")
per_selected = st.selectbox("Periode :",["quarterly", "yearly"],index=0 ,key="periode_bump")
df_bump = pd.DataFrame()
periode = 'q'
if per_selected == 'yearly':
    periode = 'y'
for kb in kabs:
    temp = st.session_state[f'df_adhb_{periode}_{kb}'].loc[komp_selected]
    temp["id"] = kb
    df_bump  = pd.concat([df_bump,temp],axis=1, ignore_index=True)
df_bump = df_bump.T
df_bump.set_index("id", inplace=True)

def create_rankings(df):
    columns = df.columns
    df_rank = pd.DataFrame()
    for i, column in enumerate(columns):
        df_rank[column] = df[column].rank(ascending=False)
    return df_rank

df_rank = create_rankings(df_bump)
list_js = []
for i, kn in enumerate(kabs):
    js_bump = df_rank.iloc[i,:].reset_index()
    id = js_bump.columns[1]
    js_bump.columns = ["x","y"]
    series =  {
    "id": id,
    "data": json.loads(js_bump.to_json(orient="records"))}
    list_js.append(series)


with elements("bump"): 
    with mui.Box(sx={"height": 400 }):
        nivo.Bump(data = list_js,  endLabel = True,pointBorderWidth =1,pointSize = 10,activeLineWidth = 5,
                  activePointSize= 14, colors = {"scheme":"red_yellow_blue"},
                  endLabelPadding=0,xOuterPadding = 1,yOuterPadding= 1,margin = {"left": 40,"right": 40,"bottom":55},
                  axisBottom = {"tickRotation": 90}
                  )

#Source of growth
def plotSOG(dataset,title):
    df_bar = dataset.T.drop(dropped2)
    df_bar["root"] = root
    fig = px.bar(df_bar.reset_index(), x="root", y=selected_year, color="Komponen", title=title)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)



# plotSOG(st.session_state[f'qq_diff_{kode}'],"Source of growth (Y-on-Y)")