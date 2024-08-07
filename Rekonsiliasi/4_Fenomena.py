import json
import streamlit as st
import pandas as pd

from sqlalchemy.sql import text

import collections

users = ['6100','6101','6102','6103','6104','6105','6106',
         '6107','6108','6109','6110','6111','6112','6171','6172']
user = st.selectbox("User :",users, index=0)


real_cols = ["1. Konsumsi Rumah Tangga","    1.a. Makanan, Minuman, dan Rokok","    1.b. Pakaian dan Alas Kaki","    1.c. Perumahan, Perkakas, Perlengkapan dan Penyelenggaraan Rumah Tangga", 
"    1.d. Kesehatan dan Pendidikan","    1.e. Transportasi, Komunikasi, Rekreasi, dan Budaya","    1.f. Hotel dan Restoran","    1.g. Lainnya"
,"2. Konsumsi Lembaga Nonprofit yang Melayani Rumah Tangga","3. Konsumsi Pemerintah",
"4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)","    4.a. Bangunan","    4.b. Non-Bangunan",
"5. Perubahan Inventori","6. Ekspor","7. Impor","PDRB" 
]
def getUploadedbyKab(kab,tahun,triwulan,putaran,conn):
    quer =f"select * from putaran_stream where kode = {kab} AND tahun = {tahun} AND tw = {triwulan} AND ptrn = {putaran} order by tipe;"
    df = conn.query(quer, ttl=0)
    available = len(df) > 0
    df = df.drop(["kode","tahun","tw","ptrn","tipe"],axis = 1).T
    df.index = real_cols
    if available:
        df.columns = ["ADHB","ADHK"]
    else:
        df["ADHB"] = None
        df["ADHK"] = None
    return df
def getUploadedbyAll(tahun,triwulan,putaran,conn):
    quer =f"select * from putaran_stream where tahun = {tahun} AND tw = {triwulan} AND ptrn = {putaran} order by tipe;"
    df = conn.query(quer, ttl=0)
    return df

conn = st.connection('mysql', type='sql',ttl = 0)
df_putaran = conn.query('SELECT * from putaran;', ttl=0)
st.session_state["putaran"] = df_putaran
tahun = st.session_state["putaran"].iloc[-1, df_putaran.columns.get_loc('tahun')]
ptrn = st.session_state["putaran"].iloc[-1, df_putaran.columns.get_loc('ptrn')]
triwulan = st.session_state["putaran"].iloc[-1, df_putaran.columns.get_loc('triwulan')]
status = st.session_state["putaran"].iloc[-1, df_putaran.columns.get_loc('stat')]
probdis = st.session_state["putaran"].iloc[-1, df_putaran.columns.get_loc('metode')]
sd = st.session_state["putaran"].iloc[-1, df_putaran.columns.get_loc('sd')]
desk = st.session_state["putaran"].iloc[-1, df_putaran.columns.get_loc('deskrepansi')]

df_monitor = getUploadedbyAll(tahun,triwulan,ptrn,conn)
mot = pd.DataFrame( {"kode" : df_monitor["kode"].unique(), "stat" :True})
board = getUploadedbyKab(user,tahun,triwulan,ptrn,conn)
uploaded_path = st.file_uploader("Choose a file",type=['xls', 'xlsx'], key = 24)
st.link_button("🗃️ Download template...", "https://docs.google.com/spreadsheets/d/1SLawywdG4lhyvATIRjSpCtaGSh1LKw_U/edit?usp=sharing&ouid=105435532900242017129&rtpof=true&sd=true")
if uploaded_path is not None:
    uploaded_file = pd.read_excel(uploaded_path)
    compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
    if compare(uploaded_file.columns,["Komponen","ADHB","ADHK"] )& (len(uploaded_file) == 17):
        uploaded_file = uploaded_file.set_index("Komponen")
        board["ADHB"] = uploaded_file["ADHB"]
        board["ADHK"] = uploaded_file["ADHK"]
    else :
        st.error("Terdapat kesalahan pada template yang anda gunakan !")     

st.markdown("Data terakhir anda :")   
st.dataframe(board,height= int(35.2*(len(board)+1)))

df = pd.read_excel("D:/Data science/national account/dataset/db_fenomena.xlsx")
df = df.set_index(["komponen","pertumbuhan"])
st.dataframe(df.drop(["id_komponen","id_growth"],axis =1) ,height= int(35.2*(len(df)+1)))