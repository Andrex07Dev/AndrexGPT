import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

llm = GoogleGenerativeAI(model='gemini-pro', temperature=0.1)

prompt = ChatPromptTemplate.from_messages([
    ('system', 'You are an excellent content writer so write on a topic given by the user'),
    ('user', '{user_query}')
])

def load_users():
    users = {}
    if os.path.exists("users.txt"):
        with open("users.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                email, username, password = line.strip().split(",")
                users[email] = {"username": username, "password": password}
    return users

def save_user(email, username, password):
    with open("users.txt", "a") as file:
        file.write(f"{email},{username},{password}\n")

def check_login(email, password, users_db):
    user = users_db.get(email)
    return user and user["password"] == password

def register_user(email, password, username, users_db):
    if email in users_db:
        return False
    save_user(email, username, password)
    users_db[email] = {"username": username, "password": password}
    return True

st.set_page_config(page_title="Andrex GPT", layout="centered")

def login_page(users_db):
    st.title("Welcome to Andrex GPT - Login")
    st.markdown("""
    <style>
    .login-form {
        width: 300px;
        padding: 20px;
        border-radius: 10px;
        background-color: #f7f7f7;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .login-input {
        width: 100%;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        border: 1px solid #ccc;
    }
    .login-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
        border: none;
    }
    .login-button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)
    
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button('Login'):
        if check_login(email, password, users_db):
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            st.session_state["username"] = users_db[email]["username"]
            st.session_state["page"] = "chat"  
            st.success(f"Login successful, {st.session_state['username']}!")
        else:
            st.error("Invalid credentials. Please try again.")
    
    if st.button('Don’t have an account? Sign Up'):
        st.session_state["page"] = "signup"

def signup_page(users_db):
    st.title("Sign Up for Andrex GPT")
    st.markdown("""
    <style>
    .signup-form {
        width: 300px;
        padding: 20px;
        border-radius: 10px;
        background-color: #f7f7f7;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .signup-input {
        width: 100%;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        border: 1px solid #ccc;
    }
    .signup-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
        border: none;
    }
    .signup-button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)
    
    email = st.text_input("Email", key="signup_email")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    
    if st.button('Sign Up'):
        if register_user(email, password, username, users_db):
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            st.session_state["username"] = username
            st.session_state["page"] = "chat"  
            st.success(f"Registration successful! Welcome, {st.session_state['username']}.")
        else:
            st.error("This email is already registered.")
    
    if st.button('Already have an account? Login'):
        st.session_state["page"] = "login"

def andrex_gpt_page():
    st.title("Andrex GPT - Generate Content")
    user_query = st.text_input("What would you like to ask AndrexGPT?")
    
    if st.button('Generate'):
        response = llm.invoke(user_query)
        st.write(response)

def main():
    users_db = load_users()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["page"] = "login"  

    if st.session_state["logged_in"]:
        andrex_gpt_page()
    elif st.session_state["page"] == "login":
        login_page(users_db)
    elif st.session_state["page"] == "signup":
        signup_page(users_db)

if __name__ == "__main__":
    main()
