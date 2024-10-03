# Chat.py

import streamlit as st
from utils.connections import ConnectionManager
from utils.chatbot import ChatBotManager

def disable_warning():
    """Disable irrelevant SQLAlchemy warnings."""
    import warnings
    from sqlalchemy.exc import SAWarning
    warnings.filterwarnings("ignore", category=SAWarning, message="Did not recognize type")

def initialize_session():
    """Initializes the Streamlit session state for storing chat messages and history."""
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'connection_manager' not in st.session_state:
        st.session_state['connection_manager'] = ConnectionManager()

def initialize_database():
    """Initializes the database tables if they do not exist."""
    try:
        st.session_state['connection_manager'].init_db()
    except Exception as e:
        st.toast(f"Oops! Couldn't start the database: {e}", icon="❌")
        st.stop()

def get_app_details():
    """Retrieves the application's name and icon from secrets."""
    app_name = st.secrets.get("app", {}).get("name", "Chat with DB")
    app_icon = st.secrets.get("app", {}).get("icon", "🤖")
    return app_name, app_icon

def display_sidebar(connections):
    """Displays the sidebar for selecting database connections and restarting the chat."""
    app_name, app_icon = get_app_details()

    with st.sidebar:
        icon_html = f"<img src='{app_icon}' style='width: 30px; margin-right: 10px;'/>" if app_icon.startswith("http") else f"<span style='font-size: 30px; margin-right: 10px;'>{app_icon}</span>"
        st.markdown(f"""
            <div style='display: flex; align-items: center; margin-bottom: 30px;'>
                {icon_html}
                <h2>{app_name}</h2>
            </div>
        """, unsafe_allow_html=True)

        connection_names = [conn.name for conn in connections]
        selected_name = st.selectbox("Choose your data playground", connection_names, placeholder="Select a database...")

        if st.button("🔄 New chat", use_container_width=True):
            st.session_state['messages'] = []
            st.session_state['chat_history'] = []
            st.rerun()

    return next((conn for conn in connections if conn.name == selected_name), None)

def display_chat_history():
    """Displays the chat history using Streamlit's chat_message component."""
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input(bot_manager, prompt):
    """Handles user input, processes the question, and updates the chat history."""
    st.session_state['messages'].append({"role": "user", "content": prompt})
    bot_manager.add_user_message(prompt)

    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Doing science..."):
            bot_response = bot_manager.process_question(prompt)
            st.markdown(bot_response)
    st.session_state['messages'].append({"role": "assistant", "content": bot_response})
    bot_manager.add_ai_message(bot_response)

def main():
    """Main function orchestrating the Streamlit application."""
    app_name, app_icon = get_app_details()
    st.set_page_config(page_title=app_name, page_icon=app_icon)

    initialize_session()
    initialize_database()

    connections = st.session_state['connection_manager'].get_connections()
    if not connections:
        st.warning("🔍 Can't see any connections! \n\n ✨ Go to the 'Connections' page and make the magic happen.")
        st.stop()

    selected_connection = display_sidebar(connections)
    if not selected_connection:
        st.toast("Selected connection not found. Please select an available one.", icon="❌")
        st.stop()

    bot_manager = ChatBotManager(st.secrets)

    try:
        engine = st.session_state['connection_manager'].get_engine(selected_connection)
        if not engine:
            st.stop()
    except Exception as e:
        st.toast(f"Oops! Couldn’t get the database engine: {e}", icon="❌")
        st.stop()

    bot_manager.initialize_agent(engine)
    
    display_chat_history()
    
    prompt = st.chat_input("Ready to geek out on some data?")
    if prompt:
        handle_user_input(bot_manager, prompt)

if __name__ == "__main__":
    disable_warning()
    main()
