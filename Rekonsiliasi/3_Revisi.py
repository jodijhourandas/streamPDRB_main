import streamlit as st 
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, JsCode
import pandas as pd
from scipy.stats import norm,uniform
import plotly.graph_objects as go
import json
from streamlit_elements import elements, mui, html, nivo, sync, event
from sqlalchemy.sql import text


users = ['6100','6101','6102','6103','6104','6105','6106',
         '6107','6108','6109','6110','6111','6112','6171','6172']
user = st.selectbox("User :",users, index=0)

#Definition
real_cols = ["1. Konsumsi Rumah Tangga","    1.a. Makanan, Minuman, dan Rokok","    1.b. Pakaian dan Alas Kaki","    1.c. Perumahan, Perkakas, Perlengkapan dan Penyelenggaraan Rumah Tangga", 
"    1.d. Kesehatan dan Pendidikan","    1.e. Transportasi, Komunikasi, Rekreasi, dan Budaya","    1.f. Hotel dan Restoran","    1.g. Lainnya"
,"2. Konsumsi Lembaga Nonprofit yang Melayani Rumah Tangga","3. Konsumsi Pemerintah",
"4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)","    4.a. Bangunan","    4.b. Non-Bangunan",
"5. Perubahan Inventori","6. Ekspor","7. Impor","PDRB" 
]

black_cols = ["1. Konsumsi Rumah Tangga",
"4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)","PDRB" 
]

kabs = ['6101','6102','6103','6104','6105','6106',
         '6107','6108','6109','6110','6111','6112','6171','6172']

real_cols = ["1. Konsumsi Rumah Tangga","    1.a. Makanan, Minuman, dan Rokok","    1.b. Pakaian dan Alas Kaki","    1.c. Perumahan, Perkakas, Perlengkapan dan Penyelenggaraan Rumah Tangga", 
"    1.d. Kesehatan dan Pendidikan","    1.e. Transportasi, Komunikasi, Rekreasi, dan Budaya","    1.f. Hotel dan Restoran","    1.g. Lainnya"
,"2. Konsumsi Lembaga Nonprofit yang Melayani Rumah Tangga","3. Konsumsi Pemerintah",
"4. Pembentukan Modal Tetap Bruto (4.a. + 4.b.)","    4.a. Bangunan","    4.b. Non-Bangunan",
"5. Perubahan Inventori","6. Ekspor","7. Impor","PDRB" 
]

kodes = ['6100','6101','6102','6103','6104','6105','6106',
         '6107','6108','6109','6110','6111','6112','6171','6172']

seam_dict = {"Q-to-Q": "qq_",
             "Y-on-Y":"yy_",
             "C-to-C":"cc_",
             "Implicit Q-to-Q":"imp_yy_",
             "Implicit Y-on-Y":"imp_qq_",
             "Implicit C-to-C":"imp_cc_"}

extra_cols = ["tahun","tw","ptrn","kode","tipe"]
def get_numeric_style_with_precision(precision: int) -> dict:
    return {"type": ["numericColumn", "customNumericFormat"], "precision": precision}
PRECISION_ZERO = get_numeric_style_with_precision(0)
PRECISION_ONE = get_numeric_style_with_precision(1)
PRECISION_TWO = get_numeric_style_with_precision(2)
PINLEFT = {"pinned": "left"}
MAX_TABLE_HEIGHT = 500

# Functions
def color_row(x):
        bc = []
        for i in x.index:
            if i in black_cols:
                bc.append(f'background-color: #31333f')
            else:
                bc.append(f'background-color: white')
        return bc
def create_rankings(df):
        columns = df.columns
        df_rank = pd.DataFrame()
        for i, column in enumerate(columns):
            df_rank[column] = df[column].rank(ascending=False)
        return df_rank
def getDataStream(conn,tipe,tahun,ptrn, tw, jenis):
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
def getDataStreamDetail(conn,tipe,tahun,ptrn, tw):
    adhk_kab = conn.query(f"SELECT * from putaran_stream WHERE tipe = '{tipe}' AND  tahun = {tahun} AND tw = {tw} AND ptrn = {ptrn} ",ttl = 0)
    adhk_kab = adhk_kab.drop(["tahun","tw","ptrn","tipe"],axis=1)
    return adhk_kab
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
    
  
    st.session_state[f'df_adhb_{kode}'] = df_adhb
    st.session_state[f'df_adhk_{kode}'] = df_adhk
    st.session_state[f'df_adhb_q_{kode}'] = df_adhb_q
    st.session_state[f'df_adhk_q_{kode}'] = df_adhk_q
    st.session_state[f'df_adhb_y_{kode}'] = df_adhb_y
    st.session_state[f'df_adhk_y_{kode}'] = df_adhk_y
    st.session_state[f'qq_{kode}'] = qq
    st.session_state[f'yy_{kode}'] = yy
    st.session_state[f'qq_y_{kode}'] = qq_y
    st.session_state[f'yy_y_{kode}'] = yy_y
    st.session_state[f'cc_{kode}'] = cc
    st.session_state[f'cc_diff_{kode}'] = cc_diff  
    st.session_state[f'impli_q_{kode}'] = impli_q   
    st.session_state[f'impli_y_{kode}'] = impli_y  
    st.session_state[f'imp_qq_{kode}'] = imp_qq
    st.session_state[f'imp_yy_{kode}'] = imp_yy
    st.session_state[f'imp_qq_y_{kode}'] = imp_qq_y
    st.session_state[f'imp_yy_y_{kode}'] = imp_yy_y
    st.session_state[f'imp_cc_{kode}'] = imp_cc  
    st.session_state[f'qq_diff_{kode}'] = qq_diff
    st.session_state[f'yy_diff_{kode}'] = yy_diff
    st.session_state[f'qq_y_diff_{kode}'] = qq_y_diff
    st.session_state[f'yy_y_diff_{kode}'] = yy_y_diff
def decisionL(vec, code):
    naik_vec = vec.str.contains('🌕').values
    turun_vec =vec.str.contains('🌑').values

    temp = []
    for naik, turun in zip(naik_vec,turun_vec):
        if(naik &  turun):
            temp.append(f"{code} Naik/Turun")
        elif(naik):
            temp.append(f"{code} Naik")
        elif(turun):
            temp.append(f"{code} Turun")
        else:
            temp.append("")
    return temp

def rekonprovinsi(daftar_kab,adhb,adhk,probdis,sd,desk,isdesk,tahun, tw,putaran):
    #Parameter
    
    #Provinsi
    st.subheader('Evaluasi Provinsi', divider='rainbow')
    #Rank evaluation
    conn = st.connection('mysql', type='sql',ttl = 0 )
    adhk_ptrn = getDataStreamDetail(conn,"adhk",tahun,putaran,tw)
    adhb_ptrn = getDataStreamDetail(conn,"adhb",tahun,putaran,tw)
    adhk_kab = getDataStream(conn,"adhk",tahun,putaran,tw,"kab")
    adhb_kab = getDataStream(conn,"adhb",tahun,putaran,tw,"kab")

    for kode in kodes:
        adhk_temp = adhk[adhk.kode == int(kode)].drop(["kode","tipe"],axis = 1).set_index("periode")
        adhb_temp = adhb[adhb.kode == int(kode)].drop(["kode","tipe"],axis = 1).set_index("periode")
        adhk_temp.columns = real_cols
        adhb_temp.columns = real_cols
        adhk_temp = adhk_temp.T.reset_index().rename(columns = {"index":"Komponen"})
        adhb_temp = adhb_temp.T.reset_index().rename(columns = {"index":"Komponen"})
        if kode == "6100":
            adhk_temp[f"{tahun}Q{tw}"] = adhk_ptrn[adhk_ptrn.kode == int(kode)].drop("kode",axis =1).T.values
            adhb_temp[f"{tahun}Q{tw}"] = adhb_ptrn[adhb_ptrn.kode == int(kode)].drop("kode",axis =1).T.values
        loading_first(kode,adhb_temp,adhk_temp)


    for kode in kodes:
        adhk_temp = adhk[adhk.kode == int(kode)].drop(["kode","tipe"],axis = 1).set_index("periode")
        adhb_temp = adhb[adhb.kode == int(kode)].drop(["kode","tipe"],axis = 1).set_index("periode")
        adhk_temp.columns = real_cols
        adhb_temp.columns = real_cols
        adhk_temp = adhk_temp.T.reset_index().rename(columns = {"index":"Komponen"})
        adhb_temp = adhb_temp.T.reset_index().rename(columns = {"index":"Komponen"})
        if kode == "6100":
            adhk_temp[f"{tahun}Q{tw}"] = adhk_kab.T.values
            adhb_temp[f"{tahun}Q{tw}"] = adhb_kab.T.values
        else:
            adhk_temp[f"{tahun}Q{tw}"] = adhk_ptrn[adhk_ptrn.kode == int(kode)].drop("kode",axis =1).T.values
            adhb_temp[f"{tahun}Q{tw}"] = adhb_ptrn[adhb_ptrn.kode == int(kode)].drop("kode",axis =1).T.values

        loading_first(f'{kode}_rev',adhb_temp,adhk_temp)

    
    #Create bump chart
    st.markdown("**Bump Chart Evaluasi Ranking Komponen PDRB**")
    komp_selected = st.selectbox("Komponen :",real_cols,index=16)
    df_bump = pd.DataFrame()
    ad_select = st.selectbox("Dasar Harga:",["adhb","adhk"],index=0,key = 45646)
    for kb in kabs:
        temp = st.session_state[f'df_{ad_select}_q_{kb}_rev'].loc[komp_selected]
        temp["id"] = kb
        df_bump  = pd.concat([df_bump,temp],axis=1, ignore_index=True)
    df_bump = df_bump.T

    df_bump.set_index("id", inplace=True)



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

    df_bump_gr = pd.DataFrame()
    for kb in kabs:
        temp = st.session_state[f'yy_{kb}_rev'].T.loc[komp_selected]
        temp["id"] = kb
        df_bump_gr  = pd.concat([df_bump_gr,temp],axis=1, ignore_index=True)
    df_bump_gr = df_bump_gr.T
    
    df_bump_gr.set_index("id", inplace=True)

    st.markdown("**Bump Chart Evaluasi Ranking Growth Y-On-Y**")
    df_rank_gr = create_rankings(df_bump_gr)
    list_js_gr = []
    for i, kn in enumerate(kabs):
        js_bump = df_rank_gr.iloc[i,:].reset_index()
        id = js_bump.columns[1]
        js_bump.columns = ["x","y"]
        series =  {
        "id": id,
        "data": json.loads(js_bump.to_json(orient="records"))}
        list_js_gr.append(series)

    
    with elements("bump_2"): 
        with mui.Box(sx={"height": 400 }):
            nivo.Bump(data = list_js_gr,  endLabel = True,pointBorderWidth =1,pointSize = 10,activeLineWidth = 5,
                    activePointSize= 14, colors = {"scheme":"red_yellow_blue"},
                    endLabelPadding=0,xOuterPadding = 1,yOuterPadding= 1,margin = {"left": 40,"right": 40,"bottom":55},
                    axisBottom = {"tickRotation": 90}
                    )

    #Data evaluation deskrepansi
    st.markdown("**Tabel Diskrepansi PDRB Kabupaten dan Provinsi**")
    adhk_kab = getDataStream(conn,"adhk",tahun,putaran,tw,"kab")
    adhb_kab = getDataStream(conn,"adhb",tahun,putaran,tw,"kab")
    adhk_prov = getDataStream(conn,"adhk",tahun,putaran,tw,"prov")
    adhb_prov = getDataStream(conn,"adhb",tahun,putaran,tw,"prov")

    df = pd.concat([adhb_kab,adhb_prov,adhk_kab,adhk_prov],axis = 1)
    df.index = real_cols
    df.columns = ["adhb_kab","adhb_prov","adhk_kab","adhk_prov"]
    df["desk_adhb"] = 100*(df["adhb_kab"]-df["adhb_prov"])/df["adhb_prov"]
    df["desk_adhk"] = 100*(df["adhk_kab"]-df["adhk_prov"])/df["adhk_prov"]


    bol_adhb = ((df.desk_adhb>=desk) | (df.desk_adhb<=-desk))
    bol_adhk = ((df.desk_adhk >=desk) | (df.desk_adhk <=-desk))
    
    #draw_grid( df.reset_index().round(2), formatter_cells)

    st.dataframe(df.style.applymap(lambda x: f"background-color: {'gold' if (x>=desk or x<=-desk)  else 'white'}", subset=['desk_adhk','desk_adhb'])
    ,height= int(35.2*(len(df)+1)))

    # Indikator
    #st.markdown("**Tabel Indikator Pertumbuhan Ekonomi**")
    seams = ["qq_","yy_","cc_","imp_yy_","imp_qq_","imp_cc_"]
    #selected = st.selectbox('Pilih mode', list(seam_dict.keys()), index=0)
    selected = seam_dict["Y-on-Y"]
    for seam in seams:
        fin = pd.DataFrame()
        temp = st.session_state[f"{seam}6100"].T.iloc[:,-1:]
        temp.columns = [f'6100_prov']
        fin = pd.concat([fin,temp],axis = 1)
        for kode in kodes:
            temp = st.session_state[f"{seam}{kode}_rev"].T.iloc[:,-1:]
            temp.columns = [kode]
            fin = pd.concat([fin,temp],axis = 1)
            st.session_state[f"{seam}_rec"] = fin

    #st.dataframe(st.session_state[f"{selected}_rec"],height= int(35.2*(len(st.session_state[f"{selected}_rec"])+1)) )



    # df_prob = pd.DataFrame()
    # for idx in range(17):
    #     datas = st.session_state[f"{selected}_rec"]
    #     mean = datas.iloc[idx,0]
    #     vec = datas.iloc[idx,2:].values
    #     coln = datas.index[idx]
    #     if probdis == "Normal":
    #         t_prob = pd.DataFrame({coln : norm(mean, sd).cdf(vec)})
    #     else:
    #         t_prob = pd.DataFrame({coln : uniform(mean-sd, 2*sd).cdf(vec)})
    #     df_prob  = pd.concat([df_prob,t_prob], axis =1)

    # df_prob = df_prob.T
    # df_prob.columns = datas.columns[2:]



    #decision

    for seam in seams:
        df_prob_des = pd.DataFrame()
        for idx in range(17):
            datas = st.session_state[f"{seam}_rec"]
            mean = datas.iloc[idx,0]
            vec = datas.iloc[idx,2:].values
            coln = datas.index[idx]
            if probdis == "Normal":
                t_prob = pd.DataFrame({coln : norm(mean, sd).cdf(vec)})
            else:
                t_prob = pd.DataFrame({coln : uniform(mean-sd, 2*sd).cdf(vec)})
            df_prob_des  = pd.concat([df_prob_des,t_prob], axis =1)
        df_prob_des = df_prob_des.T
        df_prob_des.columns = datas.columns[2:]
    
        if probdis == "Normal":
            df_new = df_prob_des.apply(pd.cut,
                        bins = [-0.1, 0.25,0.75,1.1],
                        labels=[f'🌕',f'🌓',f'🌑']
                        )
        else :
            df_new = df_prob_des.apply(pd.cut,
                        bins = [-0.1, 0.000001,0.9999999,1.1],
                        labels=[f'🌕',f'🌓',f'🌑']
                        )
        st.session_state[f"{seam}_des"] = df_new

        df_direct = st.session_state[f"{seam}_rec"].iloc[:,2:].multiply(st.session_state[f"{seam}_rec"].iloc[:,0],axis = "index")
        df_direct = df_direct.apply(pd.cut,
                        bins = [-10000000,0,10000000],
                        labels=[True,False]
                        )
        st.session_state[f"{seam}_direct"] = df_direct



    # Evaluasi kabupaten
    st.subheader('Evaluasi Kabupaten', divider='rainbow')

    kab = st.selectbox('Pilih Kabupaten :', daftar_kab, index=0)

    st.markdown("**Tabel Revisi Komponen PDRB**")
    df_res = pd.DataFrame(columns= ['Q-to-Q','Y-on-Y','C-to-C',
                                    'Imp Q-to-Q','Imp Y-on-Y','Imp C-to-C',
                                    ]
    )
    df_res['Q-to-Q'] = st.session_state[f"qq__des"][kab]
    df_res['Y-on-Y'] = st.session_state[f"yy__des"][kab]
    df_res['C-to-C'] = st.session_state[f"cc__des"][kab]
    df_res['Imp Q-to-Q'] = st.session_state[f"imp_qq__des"][kab]
    df_res['Imp Y-on-Y'] = st.session_state[f"imp_yy__des"][kab]
    df_res['Imp C-to-C'] = st.session_state[f"imp_cc__des"][kab]


    adhk_vec = df_res['Q-to-Q'].astype(str) +df_res['Y-on-Y'].astype(str)+df_res['C-to-C'].astype(str)
    adhb_vec  = df_res['Imp Q-to-Q'].astype(str) +df_res['Imp Y-on-Y'].astype(str)+df_res['Imp C-to-C'].astype(str)

    df_res['ADHK Decison'] = decisionL(adhk_vec,"ADHK")
    df_res['ADHB Decison'] = decisionL(adhb_vec,"ADHB")


    df_res_dir = pd.DataFrame(columns= ['Q-to-Q','Y-on-Y','C-to-C',
                                    'Imp Q-to-Q','Imp Y-on-Y','Imp C-to-C',
                                    ]
    )
    df_res_dir['Q-to-Q'] = st.session_state[f"qq__direct"][kab]
    df_res_dir['Y-on-Y'] = st.session_state[f"yy__direct"][kab]
    df_res_dir['C-to-C'] = st.session_state[f"cc__direct"][kab]
    df_res_dir['Imp Q-to-Q'] = st.session_state[f"imp_qq__direct"][kab]
    df_res_dir['Imp Y-on-Y'] = st.session_state[f"imp_yy__direct"][kab]
    df_res_dir['Imp C-to-C'] = st.session_state[f"imp_cc__direct"][kab]

    df_res_dir = df_res_dir.T
    temp = []
    for cola in df_res_dir.columns:
        temp.append(df_res_dir.index[df_res_dir[cola]].tolist())
    print(temp)
    df_res['Beda Arah'] = temp

    if (isdesk == "True"):
        df_res['ADHK Decison'] = df_res['ADHK Decison'][bol_adhk]
        df_res['ADHB Decison'] = df_res['ADHB Decison'][bol_adhb]
        df_res.fillna("",inplace=True)
    st.dataframe(df_res,height= int(35.2*(len(df_res)+1)))


    st.markdown("**Tabel Perbandingan Indikator PDRB Provinsi dan Kabupaten**")
    df_eval = pd.DataFrame(columns= ['Kab Q-to-Q','Prov Q-to-Q','Kab Y-on-Y','Prov Y-on-Y','Kab C-to-C','Prov C-to-C',
                                    'Kab Imp Q-to-Q','Prov Imp Q-to-Q','Kab Imp Y-on-Y','Prov Imp Y-on-Y','Kab Imp C-to-C','Prov Imp C-to-C',
                                    
                                    ]
    )
    df_eval['Kab Q-to-Q'] = st.session_state[f"qq_{kab}_rev"].T.iloc[:,-1:]
    df_eval['Prov Q-to-Q'] = st.session_state[f"qq__rec"].iloc[:,0]
    df_eval['Kab Y-on-Y'] = st.session_state[f"yy_{kab}_rev"].T.iloc[:,-1:]
    df_eval['Prov Y-on-Y'] = st.session_state[f"yy__rec"].iloc[:,0]
    df_eval['Kab C-to-C'] = st.session_state[f"cc_{kab}_rev"].T.iloc[:,-1:]
    df_eval['Prov C-to-C'] = st.session_state[f"cc__rec"].iloc[:,0]

    df_eval['Kab Imp Q-to-Q'] = st.session_state[f"imp_qq_{kab}_rev"].T.iloc[:,-1:]
    df_eval['Prov Imp Q-to-Q'] = st.session_state[f"imp_qq__rec"].iloc[:,0]
    df_eval['Kab Imp Y-on-Y'] = st.session_state[f"imp_yy_{kab}_rev"].T.iloc[:,-1:]
    df_eval['Prov Imp Y-on-Y'] = st.session_state[f"imp_yy__rec"].iloc[:,0]
    df_eval['Kab Imp C-to-C'] = st.session_state[f"imp_cc_{kab}_rev"].T.iloc[:,-1:]
    df_eval['Prov Imp C-to-C'] = st.session_state[f"imp_cc__rec"].iloc[:,0]

    st.dataframe(df_eval,height= int(35.2*(len(df_eval)+1)))


    # Graphing

    st.markdown("**Barplot growth Provinsi dan Kabupaten :**")
    mode = st.selectbox("Mode : ", ["Q-to-Q", "Y-on-Y","C-to-C","Imp Q-to-Q", "Imp Y-on-Y","Imp C-to-C"],index=0)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_eval.index.tolist(),
        x=df_eval[f'Kab {mode}'].tolist(),
        name='Nilai Kabupaten',
        marker_color='#f9c33c',
        orientation='h'
    ))
    fig.add_trace(go.Bar(
        y=df_eval.index.tolist(),
        x=df_eval[f'Prov {mode}'].tolist(),
        name='Nilai Provinsi',
        marker_color='#321b41',
        orientation='h'
    ))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(barmode='group', xaxis_tickangle=-90, yaxis=dict(autorange='reversed'))
    st.plotly_chart(fig, use_container_width=True)
    return df_res,df_eval,df


@st.dialog("Simulasi PDRB", width = 'large' ) 
@st.fragment
def simulate_ptrn(edit_df,adhk,adhb,kab,df):
    edit_df["ADHK New"] = edit_df["ADHK"]
    edit_df["ADHB New"] = edit_df["ADHB"]  

    edit_df["ADHB New"].loc[real_cols[0]] = edit_df["ADHB New"].loc[real_cols[0]] +edit_df["ADHB Adj"].loc[real_cols[1]]+edit_df["ADHB Adj"].loc[real_cols[2]]
    + edit_df["ADHB Adj"].loc[real_cols[3]]+edit_df["ADHB Adj"].loc[real_cols[4]]+edit_df["ADHB Adj"].loc[real_cols[5]]+edit_df["ADHB Adj"].loc[real_cols[6]] +edit_df["ADHB Adj"].loc[real_cols[7]]
    
    edit_df["ADHK New"].loc[real_cols[0]] = edit_df["ADHK New"].loc[real_cols[0]] +edit_df["ADHK Adj"].loc[real_cols[1]]+edit_df["ADHK Adj"].loc[real_cols[2]]
    + edit_df["ADHK Adj"].loc[real_cols[3]]+edit_df["ADHK Adj"].loc[real_cols[4]]+edit_df["ADHK Adj"].loc[real_cols[5]]+edit_df["ADHK Adj"].loc[real_cols[6]] +edit_df["ADHB Adj"].loc[real_cols[7]]
    
    edit_df["ADHK New"] = edit_df["ADHK"]+edit_df["ADHK Adj"]
    edit_df["ADHB New"] = edit_df["ADHB"]+edit_df["ADHB Adj"]
    edit_df["ADHK New"].loc["PDRB"]  = edit_df["ADHK"].loc["PDRB"] + edit_df["ADHK Adj"].sum()
    edit_df["ADHB New"].loc["PDRB"]  = edit_df["ADHB"].loc["PDRB"] + edit_df["ADHB Adj"].sum()

    adhk_temp = adhk[adhk.kode == int(kab)].drop(["kode","tipe"],axis = 1).set_index("periode")
    adhb_temp = adhb[adhb.kode == int(kab)].drop(["kode","tipe"],axis = 1).set_index("periode")
    adhk_temp.columns = real_cols
    adhb_temp.columns = real_cols
    adhk_temp = adhk_temp.T.reset_index().rename(columns = {"index":"Komponen"})
    adhb_temp = adhb_temp.T.reset_index().rename(columns = {"index":"Komponen"})
    adhk_temp[f"{tahun}Q{triwulan}"] = edit_df["ADHK New"].values
    adhb_temp[f"{tahun}Q{triwulan}"] = edit_df["ADHB New"].values

    loading_first(f'{kab}_rev_sim',adhb_temp,adhk_temp)

    #st.dataframe( st.session_state[f"df_adhk_q_{kab}_rev_sim"])
    #st.dataframe( st.session_state[f"qq_{kab}_rev_sim"])
    
    edit_df['Kab Q-to-Q'] = st.session_state[f"qq_{kab}_rev_sim"].T.iloc[:,-1:]
    edit_df['Prov Q-to-Q'] = st.session_state[f"qq__rec"].iloc[:,0]
    edit_df['Arah Q-to-Q'] = pd.cut(edit_df['Kab Q-to-Q'].values *edit_df['Prov Q-to-Q'].values,bins = [-10000000,0,10000000],
                    labels=[True,False])
    
    edit_df['Kab Y-on-Y'] = st.session_state[f"yy_{kab}_rev_sim"].T.iloc[:,-1:]
    edit_df['Prov Y-on-Y'] = st.session_state[f"yy__rec"].iloc[:,0]
    edit_df['Arah Y-on-Y'] =  pd.cut(edit_df['Kab Y-on-Y'].values *edit_df['Prov Y-on-Y'].values,bins = [-10000000,0,10000000],
                    labels=[True,False])
    
    edit_df['Kab C-to-C'] = st.session_state[f"cc_{kab}_rev_sim"].T.iloc[:,-1:]
    edit_df['Prov C-to-C'] = st.session_state[f"cc__rec"].iloc[:,0]
    edit_df['Arah C-to-C'] =  pd.cut(edit_df['Kab C-to-C'].values *edit_df['Prov C-to-C'].values,bins = [-10000000,0,10000000],
                    labels=[True,False])

    edit_df['Kab Imp Q-to-Q'] = st.session_state[f"imp_qq_{kab}_rev_sim"].T.iloc[:,-1:]
    edit_df['Prov Imp Q-to-Q'] = st.session_state[f"imp_qq__rec"].iloc[:,0]
    edit_df['Arah Imp Q-to-Q'] =  pd.cut(edit_df['Kab Imp Q-to-Q'].values *edit_df['Prov Imp Q-to-Q'].values,bins = [-10000000,0,10000000],
                    labels=[True,False])

    edit_df['Kab Imp Y-on-Y'] = st.session_state[f"imp_yy_{kab}_rev_sim"].T.iloc[:,-1:]
    edit_df['Prov Imp Y-on-Y'] = st.session_state[f"imp_yy__rec"].iloc[:,0]
    edit_df['Arah Imp Y-on-Y'] =  pd.cut(edit_df['Kab Imp Y-on-Y'].values *edit_df['Prov Imp Y-on-Y'].values,bins = [-10000000,0,10000000],
                    labels=[True,False])
    
    edit_df['Kab Imp C-to-C'] = st.session_state[f"imp_cc_{kab}_rev_sim"].T.iloc[:,-1:]
    edit_df['Prov Imp C-to-C'] = st.session_state[f"imp_cc__rec"].iloc[:,0]
    edit_df['Arah Imp C-to-C'] =  pd.cut(edit_df['Kab Imp C-to-C'].values *edit_df['Prov Imp C-to-C'].values,bins = [-10000000,0,10000000],
                    labels=[True,False])
    
    #Arah
    list_growth = ["Q-to-Q", "Y-on-Y","C-to-C","Imp Q-to-Q", "Imp Y-on-Y","Imp C-to-C"]
    df_res_dir_t = pd.DataFrame(columns= ['Q-to-Q','Y-on-Y','C-to-C',
                                'Imp Q-to-Q','Imp Y-on-Y','Imp C-to-C',
                                ]
)

    df_res_dir_t['Q-to-Q'] = edit_df['Arah Q-to-Q']
    df_res_dir_t['Y-on-Y'] = edit_df['Arah Y-on-Y']
    df_res_dir_t['C-to-C'] = edit_df['Arah C-to-C']
    df_res_dir_t['Imp Q-to-Q'] = edit_df['Arah Imp Q-to-Q']
    df_res_dir_t['Imp Y-on-Y'] = edit_df['Arah Imp Y-on-Y']
    df_res_dir_t['Imp C-to-C'] = edit_df['Arah Imp C-to-C']
    df_res_dir_t = df_res_dir_t.T
    temp = []
    for cola in df_res_dir_t.columns:
        temp.append(df_res_dir_t.index[df_res_dir_t[cola]].tolist())

    #Tabel diskrepansi
    edit_df['Beda Arah'] = temp

    df_deskre = df
    df_deskre["adhk_kab"]  = df_deskre["adhk_kab"] + edit_df["ADHK Adj"]
    df_deskre["adhb_kab"]  = df_deskre["adhb_kab"] + edit_df["ADHB Adj"]
    edit_df["desk_adhk"] = 100*(df_deskre["adhk_prov"]-df_deskre["adhk_kab"])/df_deskre["adhk_prov"]
    edit_df["desk_adhb"] = 100*(df_deskre["adhb_prov"]-df_deskre["adhb_kab"])/df_deskre["adhb_prov"]
    f = {'A':'{:.2f}'}

    #Tabel growth
    res_gr = pd.DataFrame(columns=list_growth, index = edit_df.index)
    sd = 5
    for indic in list_growth:
        for i in range(17):
            vec = edit_df[f'Kab {indic}'][i]
            mean = edit_df[f'Prov {indic}'][i]
            res_gr[f'{indic}'][i] = norm(mean-sd, 2*sd).cdf(vec)
    res_gr = res_gr.apply(pd.cut,
                    bins = [-0.1, 0.25,0.75,1.1],
                    labels=[f'🌕',f'🌓',f'🌑']
                    )
    edit_df = pd.concat([edit_df,res_gr],axis = 1)
    
    # Editor coloring
    df_show = edit_df[["ADHK New","ADHB New","desk_adhk","desk_adhb","Q-to-Q", "Y-on-Y","C-to-C","Imp Q-to-Q", "Imp Y-on-Y","Imp C-to-C","Beda Arah"]]
    df_show = df_show.style.format(f).applymap(lambda x: f"background-color: {'gold' if (x>=5 or x<=-5)  else 'white'}", subset=['desk_adhk','desk_adhb'])
    df_show = df_show.applymap(lambda x: f"background-color: {'gold' if (x>=5 or x<=-5)  else 'white'}", subset=['desk_adhk','desk_adhb'])
    
    st.dataframe(df_show,height= int(35.2*(len(df_eval)+1)))
    st.markdown("**Barplot growth Provinsi dan Kabupaten :**")
    
    plotCompare(edit_df,list_growth)
    #Bump chart
    st.markdown("**Bump Chart Evaluasi Ranking Komponen PDRB :**")
    komp_selected = st.selectbox("Komponen:",real_cols,index=16)
    ad_select = st.selectbox("Dasar Harga:",["adhb","adhk"],index=1)
    df_bump = pd.DataFrame()
    for kb in kabs:
        if kb == kab:
            temp = st.session_state[f'df_{ad_select}_q_{kb}_rev_sim'].loc[komp_selected]
        else:
            temp = st.session_state[f'df_{ad_select}_q_{kb}_rev'].loc[komp_selected]
        temp["id"] = kb
        df_bump  = pd.concat([df_bump,temp],axis=1, ignore_index=True)
    df_bump = df_bump.T
    df_bump.set_index("id", inplace=True)

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


    with elements("bump_2"): 
        with mui.Box(sx={"height": 400 }):
            nivo.Bump(data = list_js,  endLabel = True,pointBorderWidth =1,pointSize = 10,activeLineWidth = 5,
                    activePointSize= 14, colors = {"scheme":"red_yellow_blue"},
                    endLabelPadding=0,xOuterPadding = 1,yOuterPadding= 1,margin = {"left": 40,"right": 40,"bottom":55},
                    axisBottom = {"tickRotation": 90},useMesh = True
                    )

@st.dialog("Edit Parameter", width = 'large' )
def edit_parameter(conn,tahun,triwulan,putaran,metode_value,sd_value, deks_value,isdesk_value):  
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
        metode_idx = 0
        if metode_value != "Normal":
            metode_idx = 1
        metode = st.selectbox("Metode :",["Normal", "Uniform"],index=metode_idx)
    with col5:
        sd = st.number_input("SD", value=sd_value)
    with col6:
        desk = st.number_input("Deskrepansi", value=deks_value)
    is_desk = st.checkbox("Deskrepansi Only?",value=(isdesk_value == "True"))  
    if st.button("Submit"):
        quer = f'''Update putaran SET metode = '{metode}' , sd = {sd},deskrepansi= {desk} , disk_only ='{is_desk}'
        WHERE tahun = {tahun} AND triwulan = {triwulan} AND ptrn = {putaran}
        '''
        with conn.session as session:
            session.execute(text(quer))
            session.commit()
            st.rerun()




def plotCompare(edit_df,list_growth):
    mode = st.selectbox("Growth : ", list_growth,index=0)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=edit_df.index.tolist(),
        x=edit_df[f'Kab {mode}'].tolist(),
        name='Nilai Kabupaten',
        marker_color='#f9c33c',
        orientation='h'
    ))
    fig.add_trace(go.Bar(
        y=edit_df.index.tolist(),
        x=edit_df[f'Prov {mode}'].tolist(),
        name='Nilai Provinsi',
        marker_color='#321b41',
        orientation='h'
    ))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(barmode='group', xaxis_tickangle=-90, yaxis=dict(autorange='reversed'))
    st.plotly_chart(fig, use_container_width=True)


def pdrbCalculator(df):
    with st.form("calculator"):
        col1,col2,col3 = st.columns(3)
        with col1:
            komps = st.selectbox("Komponen :",real_cols, key = 454)
        with col2:
            harga = st.selectbox("Komponen :",["ADHB","ADHK"], key = 354)
        with col3:
            st.markdown(f"Decision : ")

        adj = st.slider("How old are you?", 0, 130, 25)
        
        col1,col2 = st.columns(2)
        with col1:
            st.markdown(f"{df.loc[komps,harga]}")

        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("slider")
#Check monitoring
pd.options.display.float_format = '${:,.2f}'.format

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
isdesk = st.session_state["putaran"].iloc[-1, df_putaran.columns.get_loc('disk_only')]

df = conn.query('SELECT * from pdrb;',ttl = 0)
adhk = df[df.tipe == "adhk"]
adhb = df[df.tipe == "adhb"]

if status == "uploading":
    st.info("Proses Rekonsiliasi Menunggu Seluruh Kabupaten Mengunggah PDRB...")
#Connection to sql
if (user == '6100')&(status == "revisi provinsi"):
    if st.button("Edit Parameter Rekonsiliasi...", type="primary"):
        edit_parameter(conn,tahun,triwulan,ptrn,probdis,sd,desk,isdesk)
    rekonprovinsi(kabs,adhb,adhk,probdis,sd,desk,isdesk,tahun,triwulan,ptrn)
if (user == '6100')&(status == "revisi kabupaten"):
    rekonprovinsi(kabs,adhb,adhk,probdis,sd,desk,isdesk,tahun,triwulan,ptrn)
if (user != '6100')&(status == "revisi kabupaten"):
    
    df_res,df_eval,df = rekonprovinsi([user],adhb,adhk,probdis,sd,desk,isdesk,tahun,triwulan,ptrn)

    st.subheader('Simulasi Rekonsiliasi : ', divider='rainbow')
    st.markdown("**PDRB Previous :**")
    table_pdrb = {
    "Tabel 1. PDRB ADHB Menurut Pengeluaran (Triwulan)": st.session_state[f'df_adhb_q_{user}_rev'],
    "Tabel 2. PDRB ADHK Menurut Pengeluaran (Triwulan)": st.session_state[f'df_adhk_q_{user}_rev']}

    table_selected = st.selectbox(
            "Pilih Tabel :",
        table_pdrb.keys())
    years = st.session_state[f'df_adhb_q_{user}_rev'].columns.str[:4].unique()

    options = st.multiselect("Pilih Tahun :",
        years,default=years.to_list()[-2:]
        )
    rexy = '|'.join(str(x) for x in options)
    if not options:
        rexy = "1000"
    df_tab = table_pdrb[table_selected].filter(regex = rexy,axis =1)
    st.dataframe(df_tab,height= int(35.2*(len(df_tab)+1)))

    


    #Hasil simulasi
    st.markdown("**PDRB Simulator :**")
    df_simulasi = pd.DataFrame()
    df_simulasi["ADHK"] = st.session_state[f"df_adhk_q_{user}_rev"].iloc[:,-1:]
    df_simulasi["ADHK Decision"] =df_res['ADHK Decison']
    df_simulasi["ADHK Adj"] = 0
    df_simulasi["ADHB"] = st.session_state[f"df_adhb_q_{user}_rev"].iloc[:,-1:]
    df_simulasi["ADHB Decision"] =df_res['ADHB Decison']
    df_simulasi["ADHB Adj"] = 0
    df_simulasi['Beda Arah'] = df_res['Beda Arah']
    st.session_state["df_simulasi"] = df_simulasi
    col_disable = ["ADHK","ADHB","ADHK Decision","ADHB Decision"]

    #Hasil calculator
    st.markdown("**PDRB Calculator :**")

    pdrbCalculator(df_simulasi)

    edit_df =  st.data_editor( st.session_state["df_simulasi"].style.apply(color_row), 
                            disabled=col_disable,height= int(35.2*(len(df_eval)+1)))
    

    if st.button("Simulate"):
        simulate_ptrn(edit_df,adhk,adhk,user,df)
    

    