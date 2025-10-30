import streamlit as st
import requests
import os
import time
from streamlit.components.v1 import html as components_html

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="TaskVerse AI",
    layout="wide",
)

# --- CSS STYLING ---
st.markdown("""
    <style>
        .main > div {
            max-width: 1000px;
            padding-left: 50px;
            padding-right: 50px;
        }
        .block-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding-top: 1rem;
            padding-bottom: 0;
        }
        .stTabs {
            position: sticky;
            top: 0;
            z-index: 100;
            background-color: white;
            padding-bottom: 1rem;
        }
        .chat-wrapper {
            display: flex;
            flex-direction: column;
            height: calc(100vh - 200px);
            overflow: hidden;
        }
        .chat-scroll {
            flex: 1;
            overflow-y: auto;
            padding: 1rem 0;
            margin-bottom: 1rem;
            max-height: calc(100vh - 300px);
        }
        .chat-input {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: white;
            padding: 1rem 0;
            border-top: 1px solid #e0e0e0;
            z-index: 50;
        }
        .stChatInput {
            margin: 0 !important;
        }
        .chat-scroll::-webkit-scrollbar {
            width: 8px;
        }
        .chat-scroll::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        .chat-scroll::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        .chat-scroll::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        .stChatMessage {
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTS ---
BASE_URL = os.environ.get("BACKEND_URL", "https://taskverse-ai.onrender.com")
TASK_MANAGER_ENDPOINT = f"{BASE_URL}/walker/taskverse_ai"
GET_ALL_TASKS_ENDPOINT = f"{BASE_URL}/walker/get_all_tasks"

# --- SESSION STATE INIT ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

with st.sidebar:
    st.title("Session Management")
    if st.button("Start New Session"):
        st.session_state.session_id = ""
        st.session_state.chat_history = []
        st.success("Virtual session reset!")

# --- TITLE ---
st.title("🤖 TaskVerse AI")

# --- TABS ---
tab1, tab2 = st.tabs(["💬 Chat", "📅 Scheduled Tasks"])

# ========================
#       CHAT INTERFACE
# ========================
with tab1:
    chat_container = st.container()
    with chat_container:
        messages_container = st.container()
        with messages_container:
            st.markdown('<div id="chat-scroll" class="chat-scroll">', unsafe_allow_html=True)
            for entry in st.session_state.chat_history:
                with st.chat_message(entry["role"]):
                    st.markdown(entry["content"], unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.chat_history:
            components_html("""
                <script>
                  setTimeout(() => {
                    const el = window.parent.document.getElementById('chat-scroll');
                    if (el) { 
                      el.scrollTop = el.scrollHeight; 
                    }
                  }, 100);
                </script>
            """, height=0)

    input_container = st.container()
    with input_container:
        st.markdown('<div class="chat-input">', unsafe_allow_html=True)
        prompt = st.chat_input("Ask me anything...")
        st.markdown("</div>", unsafe_allow_html=True)

    # ✅ FIXED: Timeout-safe backend call
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        payload = {"utterance": prompt, "session_id": st.session_state.session_id or ""}

        with st.spinner("Thinking..."):
            try:
                res = requests.post(TASK_MANAGER_ENDPOINT, json=payload, timeout=25)
                res.raise_for_status()
                data = res.json()
                reports = data.get("reports", [])
                if reports:
                    message = reports[0].get("response", "")
                    session_id = reports[0].get("session_id", "")
                    st.session_state.session_id = session_id
                    st.session_state.chat_history.append({"role": "assistant", "content": message})
                else:
                    st.warning("⚠️ No response from assistant.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Backend request timed out. The server might be waking up — try again.")
            except requests.exceptions.ConnectionError:
                st.error("🌐 Could not connect to backend. Please confirm it's live on Render.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

        st.rerun()

# ========================
#    SCHEDULED TASKS
# ========================
with tab2:
    st.header("📋 All Scheduled Tasks")
    cols = st.columns([1, 3])
    with cols[0]:
        refresh = st.button("🔄 Refresh")

    should_load = st.session_state.get("_reload_tasks_once", True) or refresh
    if should_load:
        with st.spinner("Loading tasks..."):
            try:
                res = requests.post(GET_ALL_TASKS_ENDPOINT, timeout=25)
                res.raise_for_status()
                data = res.json()
                reports = data.get("reports", [])
                tasks = reports[0] if reports and isinstance(reports[0], list) else []
                if tasks:
                    import pandas as pd
                    flat_tasks = []
                    for t in tasks:
                        context = t.get('context', {})
                        flat_tasks.append({
                            'id': t.get('id', ''),
                            'task': context.get('task', ''),
                            'date': context.get('date', ''),
                            'time': context.get('time', ''),
                            'status': context.get('status', '')
                        })
                    df = pd.DataFrame(flat_tasks)
                    st.dataframe(df[['task', 'date', 'time', 'status']], use_container_width=True, hide_index=True)
                else:
                    st.info("No scheduled tasks found.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout loading tasks — backend may be slow.")
            except requests.exceptions.ConnectionError:
                st.error("🌐 Could not connect to backend — check if live.")
            except Exception as e:
                st.error(f"Failed to load tasks: {e}")

        st.session_state._reload_tasks_once = False


