import subprocess
import time
import openai
import requests
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="🦙💬 Llama 3 Chatbot")

st.title("🦙💬 Llama 3 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by Llama 3")

# -----------------------------
# LLM configuration
# -----------------------------
def config_llm3():
    if "llm3_process" not in st.session_state:
        st.session_state["llm3_process"] = subprocess.Popen("ollama serve", shell=True)
        time.sleep(2) 
        try:
            llm3_request = requests.get("http://localhost:11434").content
            status_text = llm3_request.decode("utf-8")
        except Exception as e:
            status_text = f"Error: {e}"
        st.session_state["llm3_status"] = status_text
        return "http://localhost:11434/v1" 


def system_message() -> str:
    """System-level instruction for OpenAI."""
    return "You are a helpful assistant that provide simple basic short answers to given questions"

def clear_chat_histroy():
    st.session_state['chat_history'] = [{"role": "assistant", "content": "How can I help you?"}]


def chat(messages, temp, top_p):
    openai = OpenAI(base_url="http://localhost:11434/v1", api_key="None")
    response = openai.chat.completions.create(
            model="llama3.2",
            messages=messages,
            temperature=temp,
            top_p=top_p
        )

    summary = response.choices[0].message.content
    return summary



# -----------------------------
# Sessions
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = [{"role": "assistant", "content": "How can I help you?"}]
    st.session_state.chat_history.append({"role": "assistant", "content": system_message()})

for i , msg in enumerate (st.session_state.chat_history):
    if i == 1:
        continue
    st.chat_message(msg["role"]).write(msg["content"])

if "llm3_status" not in st.session_state:
    st.session_state["llm3_status"] = "Not started"


if prompt := st.chat_input():
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.spinner("Thinking..."):
        response = chat(st.session_state['chat_history'],st.session_state["temperature"],st.session_state["top_p"])
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
    

# -----------------------------
# Streamlit App
# -----------------------------

with st.sidebar:
    st.title('🦙💬 Llama 3 Chatbot')
    st.write('This chatbot is created using the open-source Llama 3 local LLM model from Meta.')

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['llama3.2-local', 'gpt-4.1-mini', 'gemini-2.5-flash'], key='selected_model')
    if selected_model == 'llama3.2-local':
        llm3_request = config_llm3()
        llm = 'http://localhost:11434/v1'
    elif selected_model == 'gpt-4.1-mini':
        llm = 'https://api.openai.com/v1'
    elif selected_model == 'gemini-2.5-flash':
        llm = 'https://generativelanguage.googleapis.com/v1beta/openai/'
    llm_url = st.sidebar.text_input("local base url", llm)
    st.sidebar.markdown(f"`{st.session_state['llm3_status']}`")
    st.session_state["temperature"] = st.sidebar.slider("temperature", 0.01, 1.0, 0.1, 0.01)
    st.session_state["top_p"] = st.sidebar.slider("top_p", 0.01, 1.0, 0.9, 0.01)
st.sidebar.button('Clear Chat', on_click=clear_chat_histroy, icon="🧹")
st.sidebar.text_area(label="data", value=st.session_state['chat_history'])