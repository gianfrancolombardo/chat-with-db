# pages/1_Connections.py

import streamlit as st
from utils.connections import ConnectionManager, Connection

def init_connection_manager():
    """ Initializes the connection manager. """
    if 'connection_manager' not in st.session_state:
        st.session_state.connection_manager = ConnectionManager()
        try:
            st.session_state.connection_manager.init_db()
        except Exception as e:
            st.toast(f"Uh-oh! Couldn’t fire up the database: {e}", icon="⚠️")

def check_feedback_message():
    """ Checks if there is a feedback message stored in session state and displays it. """
    if 'feedback_message' in st.session_state:
        st.toast(st.session_state.feedback_message['message'], icon="✅" if st.session_state.feedback_message['success'] else "⚠️")
        del st.session_state.feedback_message

def list_connections():
    """ Displays the list of saved connections. """
    try:
        connections = st.session_state.connection_manager.get_connections()
        if connections:
            for conn in connections:
                with st.expander(f"**{conn.name}** ({conn.type})"):
                    view_connection_details(conn)
                    
                    if st.button("❌ Delete", key=f"delete_{conn.id}"):
                        delete_connection(conn.id)
        else:
            st.info("It seems there are no connections yet.")
    except Exception as e:
        st.toast(f"Error retrieving connections: {e}", icon="⚠️")

def view_connection_details(conn):
    """ Displays view of the details of a connection. """
    st.write(f"**Type:** {conn.type}")
    if conn.type == 'postgresql':
        st.write(f"**Host:** {conn.host}")
        st.write(f"**Port:** {conn.port}")
        st.write(f"**User:** {conn.user}")
        st.write(f"**Database:** {conn.database}")
    elif conn.type == 'sqlite':
        st.write(f"**Path:** {conn.path}")

def delete_connection(conn_id):
    """ Deletes a connection from the database. """
    try:
        st.session_state.connection_manager.delete_connection(conn_id)
        #st.toast("Connection deleted successfully.", icon="✅")
        st.session_state.feedback_message = {"message": "Done! The connection is gone for good.", "success": True}
        st.rerun()
    except Exception as e:
        st.toast(f"Oops! There was a problem deleting the connection: {e}", icon="⚠️")

def add_connection():
    """ Adds a new connection to the database. """
    st.subheader("Add New Connection")
    type_ = st.selectbox("Database Type", ["postgresql", "sqlite"])
    with st.form("add_connection", clear_on_submit=True):

        # Initialize all fields
        host = port = user = password = database = path = ""

        name = st.text_input("Connection Name")
        if type_ == "postgresql":
            host = st.text_input("Host", value="localhost")
            port = st.text_input("Port", value="5432")
            user = st.text_input("User")
            password = st.text_input("Password", type="password")
            database = st.text_input("Database Name")
        elif type_ == "sqlite":
            path = st.text_input("SQLite File Path")

        submitted = st.form_submit_button("➕ Add Connection")

        if submitted:
            try:
                # Validate required fields
                if not name:
                    st.toast("Connection name is required.", icon="⚠️")
                elif type_ == "postgresql" and not all([host, port, user, password, database]):
                    st.toast("All fields are required for PostgreSQL connection.", icon="⚠️")
                elif type_ == "sqlite" and not path:
                    st.toast("SQLite file path is required.", icon="⚠️")
                else:
                    # Add the connection using ConnectionManager
                    st.session_state.connection_manager.add_connection(name, type_, host, port, user, password, database, path)
                    # st.toast("Connection added successfully.", icon="✅")
                    st.session_state.feedback_message = {"message": "You did it! Connection successfully added.", "success": True}
                    st.rerun()
            except ValueError as e:
                st.toast(f"Validation error: {e}", icon="⚠️")
            except Exception as e:
                st.toast(f"Error adding connection: {e}", icon="⚠️")

def manage_connections():
    """ Print the main view. """
    st.title("Manage Connections")

    tab1, tab2 = st.tabs(["All Connections", "Create"])

    with tab1:
        list_connections()

    with tab2:
        add_connection()

def main():
    init_connection_manager()
    check_feedback_message()
    manage_connections()

if __name__ == "__main__":
    main()
