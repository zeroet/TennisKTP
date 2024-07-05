import streamlit as st
import pandas as pd
import hashlib

# 초기 사용자 데이터프레임 생성
def initialize_users():
    df = pd.DataFrame(columns=['UserID', 'Password', 'Username', 'Role', 'Approved'])
    return df

# 엑셀 파일에서 사용자 데이터 불러오기
def load_users_from_excel(filename='users.xlsx'):
    try:
        df = pd.read_excel(filename)
    except FileNotFoundError:
        df = initialize_users()
        df.to_excel(filename, index=False)
    return df

# 사용자 데이터 엑셀 파일에 저장
def save_users_to_excel(df, filename='users.xlsx'):
    df.to_excel(filename, index=False)

# 비밀번호 해싱 함수
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 로그인 기능
def login(userid, password, df):
    hashed_password = hash_password(password)
    user = df[(df['UserID'] == userid) & (df['Password'] == hashed_password) & (df['Approved'] == True)]
    if not user.empty:
        return user.iloc[0]
    else:
        return None

# 로그인 페이지
def login_page():
    users_df = load_users_from_excel()

    st.title('Login')
    userid = st.text_input('UserID')
    password = st.text_input('Password', type='password')
    if st.button('Login'):
        user = login(userid, password, users_df)
        if user is not None:
            st.session_state.logged_in = True
            st.session_state.role = user['Role']
            st.session_state.userid = user['UserID']
            st.session_state.username = user['Username']
            st.success('Login successful!')
            st.experimental_rerun()
        else:
            st.error('Invalid userID or password')

# 회원가입 페이지
def signup_page():
    users_df = load_users_from_excel()

    st.title('Sign Up')
    userid = st.text_input('New UserID')
    username = st.text_input('Username')
    password = st.text_input('New Password', type='password')
    role = 'guest'  # 기본적으로 guest로 회원가입
    if st.button('Sign Up'):
        if userid and username and password:
            hashed_password = hash_password(password)
            new_user = pd.DataFrame([[userid, hashed_password, username, role, False]], columns=['UserID', 'Password', 'Username', 'Role', 'Approved'])
            users_df = pd.concat([users_df, new_user], ignore_index=True)
            save_users_to_excel(users_df)
            st.success('Sign up successful! Waiting for admin approval.')
        else:
            st.error('Please fill out all fields.')
