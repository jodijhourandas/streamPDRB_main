import streamlit as st 
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, JsCode
from sqlalchemy.sql import text
import pandas as pd
import collections

import plotly.express as px
#Local initializaton


real_cols = ["1. Konsumsi Rumah Tangga","    1.a. Makanan, Minuman, dan Rokok","    1.b. Pakaian dan Alas Kaki","    1.c. Perumahan, Perkakas, Perlengkapan dan Penyelenggaraan Rumah Tangga", 
"    1.d. Kesehatan dan Pendidikan","    1.e. Transportasi, Komunikasi, Rekreasi, dan Budaya","    1.f. Hotel dan Restoran","    1.g. Lainnya"
,"2. Konsumsi Lembaga Nonprofit yang Melayani Rumah Tangga","3. Konsumsi Pemerintah",
"4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)","    4.a. Bangunan","    4.b. Non-Bangunan",
"5. Perubahan Inventori","6. Ekspor","7. Impor","PDRB" 
]
kabs = ['6101','6102','6103','6104','6105','6106',
         '6107','6108','6109','6110','6111','6112','6171','6172']

users = ['6100','6101','6102','6103','6104','6105','6106',
         '6107','6108','6109','6110','6111','6112','6171','6172']
user = st.selectbox("User :",users, index=0)
kab = user

extra_cols = ["tahun","tw","ptrn","kode","tipe"]
#Functions and Query
def insertStream(tahun,triwulan,putaran,metode,sd,deskrepansi,disk_only,conn):
    quer =f"INSERT INTO putaran (tahun, triwulan, ptrn,metode,sd,deskrepansi, disk_only,adm, stat) VALUES ('{tahun}', '{triwulan}', '{putaran}','{metode}',{sd},{deskrepansi},'{disk_only}', 'jodijhouranda', 'uploading');"
    with conn.session as session:
        session.execute(text(quer))
        session.commit()
def insertDf(df,kode,tahun, tw,ptrn ,model = "insert"):
    if model == 'insert':
        for col in df.columns:
            quer =f'''INSERT INTO putaran_stream (pkrt, mamin, pakaian, perumahan, kesehatan, transportasi, 
            hotel, lainnya, lnprt, kp, pmtb, bangunan, nonbangungan,
            inventori, ekspor, impor, pdrb, kode, tipe, tahun, tw,
            ptrn) VALUES ({df[col].iloc[0]},{df[col].iloc[1]},{df[col].iloc[2]},{df[col].iloc[3]},{df[col].iloc[4]},{df[col].iloc[5]},
            {df[col].iloc[6]},{df[col].iloc[7]},{df[col].iloc[8]},{df[col].iloc[9]},{df[col].iloc[10]},{df[col].iloc[11]},
            {df[col].iloc[12]},{df[col].iloc[13]},{df[col].iloc[14]},{df[col].iloc[15]},{df[col].iloc[16]},{kode},'{col.lower()}',{tahun},{tw},{ptrn});'''
            with conn.session as session:
                session.execute(text(quer))
                session.commit()
    else:
        for col in df.columns:
            quer =f'''UPDATE putaran_stream SET pkrt ={df[col].iloc[0]} , 
            mamin={df[col].iloc[1]},  pakaian={df[col].iloc[2]},perumahan={df[col].iloc[3]},
            kesehatan={df[col].iloc[4]}, transportasi={df[col].iloc[5]}, hotel={df[col].iloc[6]}, 
            lainnya={df[col].iloc[7]},lnprt={df[col].iloc[8]}, kp={df[col].iloc[9]},
            pmtb={df[col].iloc[10]}, bangunan={df[col].iloc[11]}, nonbangungan={df[col].iloc[12]},
            inventori={df[col].iloc[13]}, ekspor={df[col].iloc[14]}, impor={df[col].iloc[15]}, pdrb={df[col].iloc[16]}
            WHERE kode =  {kode} AND tipe = '{col.lower()}' AND tahun = {tahun} AND tw = {tw} AND ptrn = {ptrn};'''
            with conn.session as session:
                session.execute(text(quer))
                session.commit()

def insertPDRB(df,tahun,tw,conn):
    periode = f"{tahun}Q{tw}"
    for index, row in df.iterrows():
        quer =f'''INSERT INTO pdrb (periode, pkrt, mamin, pakaian, perumahan, kesehatan, transportasi, 
        hotel, lainnya, lnprt, kp, pmtb, bangunan, nonbangungan,
        inventori, ekspor, impor, pdrb, kode, tipe) VALUES ('{periode}',{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]}
        ,{row[8]},{row[9]},{row[10]},{row[11]},{row[12]},{row[13]},{row[14]},{row[15]},{row[16]},
        '{row[17]}','{row[18]}');'''
        with conn.session as session:
            session.execute(text(quer))
            session.commit()
     
@st.dialog("Reject Kab :")          
def deleteUploadedbyKab(tahun,triwulan,putaran,mot,conn):
    selected  = st.selectbox('Pilih Kabupaten :', mot.kode[1:], index=0,key = 134)
    if st.button("Reject",type="primary"):
        quer =f"delete from putaran_stream where kode = {selected} AND tahun = {tahun} AND tw = {triwulan} AND ptrn = {putaran};"
        with conn.session as session:
            session.execute(text(quer))
            session.commit()
            st.rerun()
def deleteProv(tahun,triwulan,putaran,conn):
    quer =f"delete from putaran_stream where kode = 6100 AND tahun = {tahun} AND tw = {triwulan} AND ptrn = {putaran};"
    with conn.session as session:
        session.execute(text(quer))
        session.commit()
        st.rerun()
def deleteLastStream(conn):
    quer =f"delete from putaran order by tahun desc,triwulan desc,ptrn desc limit 1;"
    with conn.session as session:
        session.execute(text(quer))
        session.commit()   
def updateStatus(stat,tahun,triwulan,putaran,conn):
    quer = f'''Update putaran Set stat = '{stat}' 
    WHERE tahun = {tahun} AND triwulan = {triwulan} AND ptrn = {putaran}
    '''
    with conn.session as session:
        session.execute(text(quer))
        session.commit()
        st.rerun()
def updateStatusNoRerun(stat,tahun,triwulan,putaran,conn):
    quer = f'''Update putaran Set stat = '{stat}' 
    WHERE tahun = {tahun} AND triwulan = {triwulan} AND ptrn = {putaran}
    '''
    with conn.session as session:
        session.execute(text(quer))
        session.commit()
def getLastFeature(column,conn):
    quer =f"select {column} from putaran order by tahun desc,triwulan desc,ptrn desc limit 1;"
    status = conn.query(quer, ttl=0)
    return status
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
def getNextTw(tahun,triwulan):
    if triwulan==4:
        tahun = tahun+1
        triwulan = 1
        return tahun, triwulan
    else :
        tahun = tahun
        triwulan = triwulan+1
        return tahun, triwulan
def getDataStream(conn,tipe,tahun,tw,ptrn, jenis):
    if jenis == "kab":
        adhk_kab = conn.query(f"SELECT * from putaran_stream WHERE tipe = '{tipe}' AND  tahun = {tahun} AND tw = {tw} AND ptrn = {ptrn} AND kode !='6100' ",ttl = 0)
        adhk_kab = adhk_kab.drop(extra_cols,axis=1).sum()
        adhk_kab.columns = f"{tipe}_{jenis}"
        return adhk_kab
    else :
        adhk_prov = conn.query(f"SELECT * from putaran_stream WHERE tipe = '{tipe}' AND  tahun = {tahun} AND tw = {tw} AND ptrn = {ptrn} AND kode ='6100' ",ttl = 0)
        adhk_prov = adhk_prov.drop(extra_cols,axis=1).sum()
        adhk_prov.columns = f"{tipe}_{jenis}"
        return adhk_prov  
def createButtonView(kab,stat):
    if stat:
        st.button(kab,type="primary",use_container_width=True)
    else:
        st.button(kab,use_container_width=True)

def genButtonMonitor(list_kab,list_avail):
    c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
    with c1:
        createButtonView(list_kab[0],(int(list_kab[0]) in list_avail))
    with c2:
        createButtonView(list_kab[1],(int(list_kab[1]) in list_avail))
    with c3:
        createButtonView(list_kab[2],(int(list_kab[2]) in list_avail))
    with c4:
        createButtonView(list_kab[3],(int(list_kab[3]) in list_avail))
    with c5:
        createButtonView(list_kab[4],(int(list_kab[4]) in list_avail))
    with c6:
        createButtonView(list_kab[5],(int(list_kab[5]) in list_avail))
    with c7:
        createButtonView(list_kab[6],(int(list_kab[6]) in list_avail))
@st.dialog("Failed")
def failed_putaran(msg):
    st.error(msg)
@st.dialog("Warning")
def warning_putaran(msg):
    st.warning(msg)
@st.dialog("Pembutan putaran")
def create_putaran(df_putaran,putaran):
    tahun,triwulan = getNextTw(df_putaran.tahun.iloc[-1],df_putaran.triwulan.iloc[-1])
    #st.write(f"Anda akan memulai pengisian PDRB untuk triwulan ke-{triwulan} tahun {tahun}")
    col1,col2,col3 = st.columns(3)
    with col1:
        st.markdown(f"**Tahun : {tahun}**")
    with col2:
        st.markdown(f"**Triwulan : {triwulan}**")
    with col3:
        st.markdown(f"**Putaran : {putaran}**")
    col4,col5,col6 = st.columns(3)
    with col4:
        metode = st.selectbox("Metode :",["Normal", "Uniform"])
    with col5:
        sd = st.number_input("SD", value=5)
    with col6:
        desk = st.number_input("Deskrepansi", value=5)
    is_desk = st.checkbox("Deskrepansi Only?")

    uploaded_path = st.file_uploader("Choose a file",type=['xls', 'xlsx'])
    board = getUploadedbyKab(6100,tahun,triwulan,ptrn,conn)
    if uploaded_path is not None:
        uploaded_file = pd.read_excel(uploaded_path)
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
        if compare(uploaded_file.columns,["Komponen","ADHB","ADHK"] )& (len(uploaded_file) == 17):
            uploaded_file = uploaded_file.set_index("Komponen")
            board["ADHB"] = uploaded_file["ADHB"]
            board["ADHK"] = uploaded_file["ADHK"]
        else :
            st.error("Terdapat kesalahan pada template yang anda gunakan !")     
    if st.button("Submit"):
        if board.ADHB.iloc[0] is None:
            st.warning("Anda belum mengupload data")
        else:
            insertStream(tahun,triwulan,putaran,metode,sd,desk,is_desk,conn)
            insertDf(board,6100, tahun,triwulan, ptrn)
            st.success("Anda telah berhasil menjalankan triwulan baru....")
            st.rerun()
@st.dialog("Putaran berikutnya")
def create_putaranNoFile(df_putaran,tahun,triwulan,putaran):
    #st.write(f"Anda akan memulai pengisian PDRB untuk triwulan ke-{triwulan} tahun {tahun}")
    col1,col2,col3 = st.columns(3)
    with col1:
        st.markdown(f"**Tahun : {tahun}**")
    with col2:
        st.markdown(f"**Triwulan : {triwulan}**")
    with col3:
        st.markdown(f"**Putaran : {putaran}**")
    col4,col5,col6 = st.columns(3)
    with col4:
        metode = st.selectbox("Metode :",["Normal", "Uniform"])
    with col5:
        sd = st.number_input("SD", value=5)
    with col6:
        desk = st.number_input("Deskrepansi", value=5)
    is_desk = st.checkbox("Deskrepansi Only?")
    if st.button("Submit"):
        insertStream(tahun,triwulan,putaran,metode,sd,desk,is_desk,conn)
        updateStatusNoRerun("putaran selesai",tahun,triwulan,putaran-1,conn)
        board = getUploadedbyKab(6100,tahun,triwulan,putaran-1,conn)
        insertDf(board,"6100", tahun,triwulan,putaran)
        st.success("Anda telah berhasil menjalankan triwulan baru....")
        st.rerun()
@st.dialog("Anda yakin menghapus putaran ini?")
def deletelastdialog(tahun,triwulan,ptrn,conn):
    st.info(f"Putaran {ptrn} untuk tahun {tahun} dan triwulan {triwulan} sendang berjalan!")
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        if st.button("Submit",use_container_width=True,type="primary"):
            deleteLastStream(conn)
            deleteProv(tahun,triwulan,ptrn,conn)
            st.rerun()
    with col2:
        if st.button("Cancel",use_container_width=True):
            st.rerun()

@st.dialog("Selesaikan putaran",width="large")
def selesaikanPutaran(tahun,triwulan,putaran,desk,conn):
    st.markdown("**Anda yakin menyelesaikan rekonsiliasi dengan putaran ini?**")
    #st.write(f"Anda akan memulai pengisian PDRB untuk triwulan ke-{triwulan} tahun {tahun}")
    adhk_kab = getDataStream(conn,"adhk",tahun,triwulan,putaran,"kab")
    adhb_kab = getDataStream(conn,"adhb",tahun,triwulan,putaran,"kab")
    adhk_prov = getDataStream(conn,"adhk",tahun,triwulan,putaran,"prov")
    adhb_prov = getDataStream(conn,"adhb",tahun,triwulan,putaran,"prov")
    df = pd.concat([adhb_kab,adhb_prov,adhk_kab,adhk_prov],axis = 1)
    df.index = real_cols
    df.columns = ["adhb_kab","adhb_prov","adhk_kab","adhk_prov"]
    df["desk_adhk"] = 100*(df["adhk_prov"]-df["adhk_kab"])/df["adhk_prov"]
    df["desk_adhb"] = 100*(df["adhb_prov"]-df["adhb_kab"])/df["adhb_prov"]
    st.dataframe(df.style.applymap(lambda x: f"background-color: {'gold' if (x>=desk or x<=-desk)  else 'white'}", subset=['desk_adhk','desk_adhb'])
    ,height= int(35.2*(len(df)+1)))

    df_monitor = getUploadedbyAll(tahun,triwulan,ptrn,conn)
    kode_kab = st.selectbox('Pilih Kabupaten :', kabs, index=0)
    df_up = df_monitor[df_monitor.kode == int(kode_kab)]
    available = len(df_up) > 0
    df_up = df_up.drop(["kode","tahun","tw","ptrn","tipe"],axis = 1).T
    df_up.index = real_cols
    df_up.columns = ["ADHB","ADHK"]
    st.dataframe(df_up,height= int(35.2*(len(df_up)+1)))

    st.dataframe(df_monitor)
    if st.button("Submit",type="primary"):
        insertPDRB(df_monitor,tahun,triwulan,conn)
        updateStatus("finished",tahun,triwulan,putaran,conn)
        st.rerun()
# Mulai kode
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

if user == '6100':
    st.subheader('Daftar Putaran : ', divider='rainbow')
    df_view =  st.table(st.session_state["putaran"])
    col1,col2,col3,col4,col5, col6,col7,col8= st.columns(8)
    with col1:
        if st.button("Start new quartile...", type="primary",use_container_width=True):
            if df_putaran.stat.iloc[-1] == "finished":
                create_putaran(df_putaran,1)
            else:
                failed_putaran("Anda tidak bisa membuat putaran baru sebelum menyelesaikan putaran sebelumnya!")
    with col2:
        if st.button("Delete last...",use_container_width=True,type="primary"):
            if (status == "finished") | (status == "putaran selesai"):
                failed_putaran("Anda tidak dapat menghapus putaran yang telah selesai")
            else:
                deletelastdialog(tahun,triwulan,ptrn,conn)
    with col3:
        if st.button("Previous Step",use_container_width=True):
            if status == "finished":
                warning_putaran("Silahkan memulai putaran baru terlebih dahulu!")
            elif status == "uploading":
                warning_putaran("Tekan delete untuk menghapus putaran!")
            elif status == "revisi provinsi":
                updateStatus("uploading",tahun, triwulan,ptrn,conn)
            elif status == "revisi kabupaten":
                updateStatus("revisi provinsi",tahun, triwulan,ptrn,conn)
            elif status == "putaran selesai":
                updateStatus("revisi kabupaten",tahun, triwulan,ptrn,conn)
    with col4:
        if st.button("Next Step",use_container_width=True):
            if status == "finished":
                warning_putaran("Silahkan memulai putaran baru terlebih dahulu!")
            elif status == "uploading":
                df_monitor = getUploadedbyAll(tahun,triwulan,ptrn,conn)
                if len(df_monitor["kode"].unique()) <15:
                    warning_putaran("Seluruh kabupaten belum melakukan update")
                else :
                    updateStatus("revisi provinsi",tahun, triwulan,ptrn,conn)
            elif status == "revisi provinsi":
                updateStatus("revisi kabupaten",tahun, triwulan,ptrn,conn)
            elif status == "revisi kabupaten":
                warning_putaran("Tahap selanjutnya pilih 'Next Putaran' atau 'Akhiri Rekonsiliasi'")
            else:
                warning_putaran("And di tahap terakhir pada putaran ini")
    
if (status == "revisi kabupaten") & (user == "6100"):
    with col5:
        if st.button("Next putaran...",use_container_width=True, type="primary"):
            create_putaranNoFile(df_putaran,tahun, triwulan,ptrn+1)
    with col6:
        if st.button("Akhiri rekonsiliasi...",use_container_width=True, type="primary"):
            selesaikanPutaran(tahun,triwulan,ptrn,desk,conn)
    #Monitoring upload
if (status== "uploading") & (user == "6100"):
    st.subheader('Monitoring Putaran : ', divider='rainbow')
    # counties = gpd.read_file("D:/Data science/national account/kalbar.geojson")
    # counties["kode"] = counties["ADM2_PCODE"].str[2:].astype(int)
    col1,col2 = st.columns(2)
    df_monitor = getUploadedbyAll(tahun,triwulan,ptrn,conn)
    df_monitor = df_monitor.sort_values("kode")
    mot = pd.DataFrame( {"kode" : df_monitor["kode"].unique(), "stat" :True})
    with col1:
        

        progress = ((len(mot)-1)/14)*100
        st.markdown("**Progress Upload BPS Kabupaten/Kota**")
        df = pd.DataFrame({'names' : ['progress','non'],
                        'values' :  [progress, 100 - progress]})
        fig = px.pie(df, values ='values', names = 'names',color='names', hole = 0.6,
                       color_discrete_map = {'progress':'red', 'non':'rgba(0,0,0,0)'}
                    )
        fig.update_traces(textinfo='none')
        fig.update_layout(showlegend=False,
                          annotations=[dict(text=str(round(progress,2))+"%",x=0.5, y=0.5, font_size=30, showarrow=False)]
                          )
        fig.data[0].textfont.color = 'red'
        # fig.show()
        st.plotly_chart(fig)
        genButtonMonitor(kabs[:7],mot["kode"].values)
        genButtonMonitor(kabs[7:],mot["kode"].values)
        if st.button("Reject Kabupaten..."):
            if len(mot) > 1: 
                deleteUploadedbyKab(tahun,triwulan,ptrn,mot,conn)
            else:
                warning_putaran("Tidak tersedia data di putaran ini")
    with col2:
        kode_kab = st.selectbox('Pilih Kabupaten :', kabs, index=0)
        df_up = df_monitor[df_monitor.kode == int(kode_kab)]
        available = len(df_up) > 0
        df_up = df_up.drop(["kode","tahun","tw","ptrn","tipe"],axis = 1).T
        df_up.index = real_cols
        if available:
            df_up.columns = ["ADHB","ADHK"]
        else:
            df_up["ADHB"] = None
            df_up["ADHK"] = None
        st.dataframe(df_up,height= int(35.2*(len(df_up)+1)))
        

 
    

#Uploading files
if (status == "uploading"):
    st.subheader('Upload menu: ', divider='rainbow')
    
    df_monitor = getUploadedbyAll(tahun,triwulan,ptrn,conn)
    mot = pd.DataFrame( {"kode" : df_monitor["kode"].unique(), "stat" :True})
    board = getUploadedbyKab(kab,tahun,triwulan,ptrn,conn)
    uploaded_path = st.file_uploader("Choose a file",type=['xls', 'xlsx'], key = 24)
    st.link_button("🗃️ Download template...", "https://docs.google.com/spreadsheets/d/1SLawywdG4lhyvATIRjSpCtaGSh1LKw_U/edit?usp=sharing&ouid=105435532900242017129&rtpof=true&sd=true")
    if uploaded_path is not None:
        uploaded_file = pd.read_excel(uploaded_path)
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
        if compare(uploaded_file.columns,["Komponen","ADHB","ADHK"] )& (len(uploaded_file) == 17):
            uploaded_file = uploaded_file.set_index("Komponen")
            board["ADHB"] = uploaded_file["ADHB"]
            board["ADHK"] = uploaded_file["ADHK"]
            if mot.stat[mot.kode == int(kab)].values:
                insertDf(board,kab, tahun,triwulan, ptrn,"update")
            else:
                insertDf(board,kab, tahun,triwulan, ptrn)
        else :
            st.error("Terdapat kesalahan pada template yang anda gunakan !")     

    st.markdown("Data terakhir anda :")   
    st.dataframe(board,height= int(35.2*(len(board)+1)))
    

if (status == "revisi provinsi"):
    st.info("Silahkan menuju laman revisi untuk melihat hasil rekonsiliasi")
if (status == "revisi kabupaten"):
    st.info("BPS Kabupaten sedang melakukan revisi.")
if (status == "putaran selesai"):
    st.info("Tekan 'Previous step...' untuk kembali")