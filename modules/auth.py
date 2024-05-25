import streamlit as st
import streamlit_authenticator as stauth
import sys
import os

sys.path.append(os.getcwd())
from modules.mongo import *


# MongoDB连接URI
uri = "mongodb+srv://EstarHsh:Data141592@cluster0.eelcdog.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# 连接到MongoDB
client = connect_to_mongo(uri)

# 获取集合
collection = get_collection(client)

config = find_document(collection, {'config': {'$exists': True}})
if config is None:
    raise ValueError('No matching document found')

def get_auth():
    return stauth.Authenticate(
        config['config']['credentials'],
        config['config']['cookie']['name'],
        config['config']['cookie']['key'],
        config['config']['cookie']['expiry_days'],
        config['config']['preauthorized']
    )

def get_login(authenticator):
    authenticator.login(fields={'Form name':'登录', 'Username':'用户名', 'Password':'密码', 'Login':'确认登录'})

    if st.session_state["authentication_status"]:
        st.write(f'Logged username: **{st.session_state.username}**')

    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')

    else:
        st.error('Username/password is incorrect')

def get_register(authenticator):
    try:
        # email_of_registered_user, username_of_registered_user, name_of_registered_user = 
        if authenticator.register_user(fields={'Form name':'用户注册', 'Email':'邮箱', 'Username':'用户名', 'Password':'密码', 'Repeat password':'请再次输入密码', 'Register':'确认注册'}, pre_authorization=False):
            collection.replace_one({'config': {'$exists': True}}, config)
            st.success('Registration is successful!')
    except Exception as e:
        st.error(e)

def get_logout(authenticator):
    st.markdown(f'''Welcome **{st.session_state["name"]}**''')
    authenticator.logout('退出登录',  'sidebar', key='unique_key')

# def get_reset_password(authenticator):
#     try:
#         # 重置密码
#         if authenticator.reset_password(st.session_state["username"], yields={'Form name':'重置密码', 'Current password':'旧密码', 'New password':'新密码', 'Repeat password': '请再次输入新密码', 'Reset':'确认重置'}):
#             st.write(config)
#             st.success('Password modified successfully')
#     except Exception as e:
#         st.error(e)

def get_forgot_password(authenticator):
    if not st.session_state["authentication_status"]:
        try:
            username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password(fields={'Form name':'忘记密码', 'Username':'用户名', 'Submit':'提交'})
            if username_of_forgotten_password:
                st.success('Successfully get the user info.')
                st.write('Your new random password is: ', new_random_password)
            elif username_of_forgotten_password == False:
                st.error('Username not found')
        except Exception as e:
            st.error(e)