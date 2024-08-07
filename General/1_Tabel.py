import streamlit as st 
from st_aggrid import AgGrid
import pandas as pd
import io

# buffer to use for excel writer
buffer = io.BytesIO()
real_cols = ["1. Konsumsi Rumah Tangga","    1.a. Makanan, Minuman, dan Rokok","    1.b. Pakaian dan Alas Kaki","    1.c. Perumahan, Perkakas, Perlengkapan dan Penyelenggaraan Rumah Tangga", 
"    1.d. Kesehatan dan Pendidikan","    1.e. Transportasi, Komunikasi, Rekreasi, dan Budaya","    1.f. Hotel dan Restoran","    1.g. Lainnya"
,"2. Konsumsi Lembaga Nonprofit yang Melayani Rumah Tangga","3. Konsumsi Pemerintah",
"4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)","    4.a. Bangunan","    4.b. Non-Bangunan",
"5. Perubahan Inventori","6. Ekspor","7. Impor","PDRB" 
]
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

def sog(df_diff, df_growth):
    pdrb = df_diff.PDRB
    growth = df_growth.PDRB
    res = df_diff.div(pdrb,axis = 0).mul(growth,axis = 0).round(2)
    return res

# Load data
kodes = ['6100','6101','6102','6103','6104','6105','6106',
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

all_table_nt = [f'df_adhb_q_{kode}',f'df_adhk_q_{kode}',f'df_adhb_y_{kode}',f'df_adhk_y_{kode}',f'impli_q_{kode}',f'impli_y_{kode}'
             ]

all_table_t = [f'qq_{kode}',f'yy_{kode}',
             f'cc_{kode}',f'qq_y_{kode}',f'imp_qq_{kode}',f'imp_yy_{kode}',f'imp_cc_{kode}',
             f'imp_qq_y_{kode}',f'qq_diff_{kode}',f'yy_diff_{kode}',f'cc_diff_{kode}',f'qq_diff_{kode}'
             ]

table_pdrb = {
  "Tabel 1. PDRB ADHB Menurut Pengeluaran (Triwulan)": st.session_state[f'df_adhb_q_{kode}'],
  "Tabel 2. PDRB ADHK Menurut Pengeluaran (Triwulan)": st.session_state[f'df_adhk_q_{kode}'],
  "Tabel 3. PDRB ADHB Menurut Pengeluaran (Tahunan)": st.session_state[f'df_adhb_y_{kode}'],
  "Tabel 4. PDRB ADHK Menurut Pengeluaran (Tahunan)": st.session_state[f'df_adhk_y_{kode}'],
  "Tabel 5. Pertumuhan PDRB Menurut Pengeluaran Q-to-Q (Triwulan)": st.session_state[f'qq_{kode}'].T,
  "Tabel 6. Pertumuhan PDRB Menurut Pengeluaran Y-on-Y (Triwulan)": st.session_state[f'yy_{kode}'].T,
  "Tabel 7. Pertumuhan PDRB Menurut Pengeluaran C-to-C (Triwulan)": st.session_state[f'cc_{kode}'].T,
  "Tabel 8. Pertumuhan PDRB Menurut Pengeluaran Y-on-Y (Tahunan)": st.session_state[f'qq_y_{kode}'].T,
  "Tabel 9. Indeks Implisit PDRB Pengeluaran (Triwulan)": st.session_state[f'impli_q_{kode}'],
  "Tabel 10. Indeks Implisit PDRB Pengeluaran (Tahunan)": st.session_state[f'impli_y_{kode}'],
  "Tabel 11. Pertumuhan Indeks Implisit Menurut Pengeluaran Q-to-Q (Triwulan)": st.session_state[f'imp_qq_{kode}'].T,
  "Tabel 12. Pertumuhan Indeks Implisit Menurut Pengeluaran Y-on-Y (Triwulan)": st.session_state[f'imp_yy_{kode}'].T,
  "Tabel 13. Pertumuhan Indeks Implisit Menurut Pengeluaran C-to-C (Triwulan)": st.session_state[f'imp_cc_{kode}'].T,
  "Tabel 14. Pertumuhan Indeks Implisit Menurut Pengeluaran Y-on-Y (Tahunan)": st.session_state[f'imp_qq_y_{kode}'].T,
  "Tabel 15. Sumber Pertumbuhan PDRB menurut Pengeluaran Q-to-Q (Triwulan)": st.session_state[f'qq_diff_{kode}'].T,
  "Tabel 16. Sumber Pertumbuhan PDRB menurut Pengeluaran Y-on-Y (Triwulan)": st.session_state[f'yy_diff_{kode}'].T,
  "Tabel 17. Sumber Pertumbuhan PDRB menurut Pengeluaran C-to-C (Triwulan)": st.session_state[f'cc_diff_{kode}'].T,
  "Tabel 18. Sumber Pertumbuhan PDRB menurut Pengeluaran Y-on-Y (Tahunan)": st.session_state[f'qq_diff_{kode}'].T
}

table_selected = st.selectbox(
        "Pilih Tabel :",
    table_pdrb.keys())


years = st.session_state[f'df_adhb_q_{kode}'].columns.str[:4].unique()

options = st.multiselect("Pilih Tahun :",
    years,default=years.to_list()
    )





rexy = '|'.join(str(x) for x in options)
if not options:
    rexy = "1000"
df_show = table_pdrb[table_selected].filter(regex = rexy,axis =1).reset_index()
st.dataframe(df_show,height= int(35.2*(len(df_show)+1)))


def convert_df(df):
   return df.to_csv().encode('utf-8')

col1, col2 , col3 , col4 = st.columns(4)

with col1:
    csv = convert_df(df_show)
    st.download_button(
    "Download as CSV",
    csv,
    f'{table_selected} {kode}.csv',
    "text/csv",
    key='download-csv'
    )
with col2:
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        df_show.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        download2 = st.download_button(
            label="Download as Excel",
            data=buffer,
            file_name= f'{table_selected} {kode}.xlsx',
            mime='application/vnd.ms-excel'
        )
with col3:
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        for sheet in all_table_nt:
             df = st.session_state[sheet]
             df.filter(regex = rexy,axis =1).to_excel(writer, sheet_name=sheet)

        for sheet in all_table_t:
             df = st.session_state[sheet]
             df.T.filter(regex = rexy,axis =1).to_excel(writer, sheet_name=sheet)
        writer.save()
        download2 = st.download_button(
            label="Download All Tables",
            data=buffer,
            file_name= f'Tabel turunan PDRB {kode}.xlsx',
            mime='application/vnd.ms-excel'
        )