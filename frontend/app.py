"""Streamlit chat frontend — NeoBank Support Chatbot."""

import json

import requests
import streamlit as st

st.set_page_config(page_title="NeoBank Support", page_icon="🏦", layout="centered")

# --- Config ---
API_BASE = "http://localhost:8000"

# --- Session state ---
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "pt"
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# --- Header ---
st.title("🏦 NeoBank Support")
st.caption("AI-powered customer support")

# --- Language toggle ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    lang = st.radio(
        "Language / Idioma",
        ["pt", "en"],
        index=0 if st.session_state.language == "pt" else 1,
        horizontal=True,
        key="lang_toggle",
    )
    st.session_state.language = lang

# --- Customer selection ---
if not st.session_state.session_id:
    st.subheader("Select Customer / Selecionar Cliente")
    customer_options = {
        "Maria Silva (123.456.789-00)": "11111111-1111-1111-1111-111111111111",
        "John Smith (987.654.321-00)": "22222222-2222-2222-2222-222222222222",
        "Ana Costa (456.789.123-00)": "33333333-3333-3333-3333-333333333333",
        "Carlos Pereira (321.654.987-00)": "44444444-4444-4444-4444-444444444444",
    }
    selected = st.selectbox("Customer / Cliente", list(customer_options.keys()))

    if st.button("Start Chat / Iniciar Chat"):
        customer_id = customer_options[selected]
        try:
            resp = requests.post(
                f"{API_BASE}/sessions",
                json={"customer_id": customer_id, "language": st.session_state.language},
            )
            resp.raise_for_status()
            data = resp.json()
            st.session_state.session_id = data["session_id"]
            st.rerun()
        except Exception as e:
            st.error(f"Failed to create session: {e}")

else:
    # --- Chat interface ---
    st.caption(f"Session: {st.session_state.session_id[:8]}...")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input — also handle pending prompts from Quick Actions
    prompt = st.chat_input("Type your message...")
    if st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Send to API
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                with requests.post(
                    f"{API_BASE}/chat",
                    json={"session_id": st.session_state.session_id, "message": prompt},
                    stream=True,
                    timeout=60,
                ) as resp:
                    for line in resp.iter_lines():
                        if line:
                            line = line.decode("utf-8")
                            if line.startswith("data: "):
                                data = json.loads(line[6:])
                                if data["type"] == "token":
                                    full_response += data["data"]
                                    message_placeholder.markdown(full_response + "▌")
                                elif data["type"] == "handoff":
                                    st.warning("🔄 Handoff to human agent initiated.")
                                    with st.expander("Handoff Details"):
                                        st.json(data["data"])
                                elif data["type"] == "tool":
                                    st.info(f"🔧 {data['data']}")
                                elif data["type"] == "error":
                                    st.error(f"Error: {data['data']}")
                                elif data["type"] == "done":
                                    break

                message_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"Error: {e}")
                full_response = "Sorry, an error occurred."

        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # --- Sidebar ---
    with st.sidebar:
        st.subheader("Quick Actions")
        if st.button("💰 Check Balance"):
            st.session_state.pending_prompt = "Qual é o meu saldo?"
            st.rerun()
        if st.button("📋 Recent Transactions"):
            st.session_state.pending_prompt = "Quero ver minhas transações recentes"
            st.rerun()
        if st.button("💳 My Cards"):
            st.session_state.pending_prompt = "Quais são meus cartões?"
            st.rerun()

        st.divider()
        if st.button("End Session / Encerrar"):
            st.session_state.session_id = None
            st.session_state.messages = []
            st.rerun()
