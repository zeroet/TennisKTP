import streamlit as st
from login import login_page, signup_page
from admin import admin_approval_page, admin_management_page
from tennis_ranking import tennis_ranking_page

# 로그인 상태 관리
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None

# 애플리케이션 라우팅
if not st.session_state.logged_in:
    login_page()
    signup_page()
elif st.session_state.role == 'admin':
    tennis_ranking_page()
    admin_approval_page()
    admin_management_page()
else:
    tennis_ranking_page()
