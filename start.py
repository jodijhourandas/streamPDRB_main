import streamlit as st
import streamlit_authenticator as stauth

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()

def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

dashboard = st.Page(
    "General/0_Home.py", title="Dashboard", icon=":material/dashboard:", default=True
)
tabel = st.Page("General/1_Tabel.py", title="Tabel", icon=":material/table:")
analisis = st.Page("General/2_Analize.py", title="Analisis", icon=":material/calculate:")

rekon = st.Page("Rekonsiliasi/2_Rekonsiliasi.py", title="Rekonsiliasi", icon=":material/healing:")
revisi = st.Page("Rekonsiliasi/3_Revisi.py", title="Revisi", icon=":material/bug_report:")
fenomena = st.Page("Rekonsiliasi/4_Fenomena.py", title="Fenomena", icon=":material/history:")

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Account": [logout_page],
            "General": [dashboard, tabel,analisis],
            "Rekonsiliasi": [rekon, revisi,fenomena],
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()