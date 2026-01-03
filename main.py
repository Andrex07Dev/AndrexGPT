import os
import streamlit as st
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE__API_KEY"
os.environ["LANGCHAIN_API_KEY"] = "YOUR_LANGCHAIN__API_KEY"

llm = ChatGoogleGenerativeAI(model='gemini-pro', temperature=0.1)

def load_users():
    users = {}
    if os.path.exists("users.txt"):
        with open("users.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                email, username, password, user_id = line.strip().split(",")
                users[email] = {"username": username, "password": password, "id": int(user_id)}
    return users

def save_user(email, username, password, user_id):
    with open("users.txt", "a") as file:
        file.write(f"{email},{username},{password},{user_id}\n")

def check_login(email, password, users_db):
    user = users_db.get(email)
    return user and user["password"] == password

def register_user(email, password, username, users_db, next_user_id):
    if email in users_db:
        return False
    save_user(email, username, password, next_user_id)
    users_db[email] = {"username": username, "password": password, "id": next_user_id}
    return True

st.set_page_config(page_title="Andrex GPT", layout="centered")

def login_page(users_db):
    st.title("Benvenuto ad Andrex GPT - Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button('Login'):
        if check_login(email, password, users_db):
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            st.session_state["username"] = users_db[email]["username"]
            st.session_state["page"] = "chat"
            st.success(f"Login effettuato con successo, {st.session_state['username']}!")
            st.rerun()
        else:
            st.error("Credenziali errate. Riprova.")

    if st.button('Non hai un account? Registrati'):
        st.session_state["page"] = "signup"
        st.rerun()

def signup_page(users_db, next_user_id):
    st.title("Registrati ad Andrex GPT")
    email = st.text_input("Email", key="signup_email")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")

    if st.button('Registrati'):
        if register_user(email, password, username, users_db, next_user_id):
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            st.session_state["username"] = username
            st.session_state["page"] = "chat"
            st.success(f"Registrazione riuscita! Benvenuto, {st.session_state['username']}.")
            st.rerun()
        else:
            st.error("Questo email è già registrato.")

    if st.button('Hai già un account? Accedi'):
        st.session_state["page"] = "login"
        st.rerun()

def gradual_response(response, container, delay=0.05):
    full_text = ""
    words = response.split()
    for word in words:
        full_text += word + " "
        container.write(full_text)
        time.sleep(delay)

def andrex_gpt_page():
    st.title("Andrex GPT - Genera Contenuto")
    user_query_input = st.text_input("Cosa vuoi chiedere ad AndrexGPT?", key="user_query_input")

    if user_query_input:
        chat_message = HumanMessage(content=user_query_input)
        response = llm.invoke([chat_message])
        response_container = st.empty()
        gradual_response(response.content, response_container)

def main():
    users_db = load_users()
    next_user_id = max([user["id"] for user in users_db.values()], default=0) + 1

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["page"] = "login"

    if st.session_state["logged_in"]:
        andrex_gpt_page()
    elif st.session_state["page"] == "login":
        login_page(users_db)
    elif st.session_state["page"] == "signup":
        signup_page(users_db, next_user_id)

if __name__ == "__main__":
    main()

