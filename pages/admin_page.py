import streamlit as st
import pandas as pd
from login import load_users_from_excel, save_users_to_excel

def admin_page():
    users_df = load_users_from_excel()

    st.title('Admin Page')
    pending_users = users_df[users_df['Approved'] == False]
    if not pending_users.empty:
        st.subheader('Pending Users')
        for index, user in pending_users.iterrows():
            st.write(f"Username: {user['Username']}, Role: {user['Role']}")
            if st.button(f'Approve {user["Username"]}', key=f'approve_{user["UserID"]}'):
                users_df.at[index, 'Approved'] = True
                save_users_to_excel(users_df)
                st.success(f'User {user["Username"]} approved')

    st.subheader('Update Role')
    username_to_update = st.selectbox('Select User', users_df['UserID'])
    new_role = st.selectbox('Select Role', ['admin', 'user', 'guest'])
    if st.button('Update Role'):
        users_df.loc[users_df['UserID'] == username_to_update, 'Role'] = new_role
        save_users_to_excel(users_df)
        st.success(f'User {username_to_update} role updated to {new_role}')

    st.subheader('Delete User')
    user_to_delete = st.selectbox('Select User to Delete', users_df['UserID'])
    if st.button('Delete User'):
        users_df = users_df[users_df['UserID'] != user_to_delete]
        save_users_to_excel(users_df)
        st.success(f'User {user_to_delete} deleted')

    # Screenshot upload section
    st.subheader('Upload Screenshot')
    uploaded_file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        with open(f"screenshots/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File uploaded successfully")

    # Display all uploaded screenshots
    st.subheader('Uploaded Screenshots')
    import os
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    screenshots = os.listdir("screenshots")
    for screenshot in screenshots:
        st.image(f"screenshots/{screenshot}")
