import streamlit as st
import pandas as pd
from login import load_users_from_excel, save_users_to_excel

# 관리자 승인 페이지
def admin_approval_page():
    users_df = load_users_from_excel()

    st.title('Admin Approval Page')
    pending_users = users_df[users_df['Approved'] == False]
    if not pending_users.empty:
        st.subheader('Pending Users')
        for index, user in pending_users.iterrows():
            st.write(f"UserID: {user['UserID']}, Username: {user['Username']}, Role: {user['Role']}")
            if st.button(f'Approve {user["UserID"]}'):
                users_df.at[index, 'Approved'] = True
                save_users_to_excel(users_df)
                st.success(f'User {user["UserID"]} approved')

# 관리자 역할 변경 및 유저 삭제 페이지
def admin_management_page():
    users_df = load_users_from_excel()

    st.title('Admin Management Page')
    st.subheader('Update Role')
    username_to_update = st.selectbox('Select User', users_df['UserID'])
    new_role = st.selectbox('Select Role', ['admin', 'user', 'guest'])
    if st.button('Update Role'):
        if new_role == 'user':
            users_df.loc[users_df['UserID'] == username_to_update, ['Role', 'Approved']] = [new_role, True]
            save_users_to_excel(users_df)
            st.success(f'User {username_to_update} role updated to {new_role} and approved')
        elif new_role == 'guest':
            users_df.loc[users_df['UserID'] == username_to_update, ['Role', 'Ranking Points', 'Wins', 'Losses', 'Draws', 'Championships', 'Approved']] = [new_role, 1000, 0, 0, 0, 0, True]
            save_users_to_excel(users_df)
            st.success(f'User {username_to_update} role updated to {new_role} and reset stats')

    st.subheader('Delete User')
    user_to_delete = st.selectbox('Select User to Delete', users_df['UserID'])
    if st.button('Delete User'):
        users_df = users_df[users_df['UserID'] != user_to_delete]
        save_users_to_excel(users_df)
        st.success(f'User {user_to_delete} deleted')

    st.subheader('Delete Guest')
    guest_to_delete = st.selectbox('Select Guest to Delete', users_df[users_df['Role'] == 'guest']['UserID'])
    if st.button('Delete Guest'):
        users_df = users_df[users_df['UserID'] != guest_to_delete]
        save_users_to_excel(users_df)
        st.success(f'Guest {guest_to_delete} deleted')
