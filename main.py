import streamlit as st
from login import login_page, signup_page
from tennis_ranking import tennis_ranking_page

def main():
    if not st.session_state.logged_in:
        hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .css-18e3th9 {padding-top: 0rem;}
        .css-1d391kg {padding-top: 3.5rem;}
        </style>
        """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)
        login_page()
    else:
        st.sidebar.title("Navigation")
        if st.session_state.role == "admin":
            page = st.sidebar.radio("Go to", ["Tennis Ranking", "Admin Page", "Logout"])
        else:
            page = st.sidebar.radio("Go to", ["Tennis Ranking", "Logout"])

        if page == "Tennis Ranking":
            tennis_ranking_page()
        elif page == "Admin Page" and st.session_state.role == "admin":
            from pages import admin_page
            admin_page.admin_page()
        elif page == "Logout":
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.userid = None
            st.session_state.username = None
            st.experimental_rerun()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None

main()
