import json
import subprocess
import time
import requests
import streamlit as st
from openai import OpenAI
import pprint

st.set_page_config(page_title="🦙💬 Llama 3 Chatbot")

st.title("🦙💬 Llama 3 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by Llama 3")

# -----------------------------
# Tools
# -----------------------------

grocery_prices = {
    "milk": 2.99,
    "bread": 1.99,
    "eggs": 3.49,
    "rice": 4.79,
    "chicken": 8.99,
    "apples": 2.49,
    "bananas": 1.29,
    "cheese": 5.99,
    "tomatoes": 2.99,
    "potatoes": 3.99
}

grocery_counts = {
    "milk": 10,
    "bread": 25,
    "eggs": 12,
    "rice": 8,
    "chicken": 5,
    "apples": 30,
    "bananas": 40,
    "cheese": 6,
    "tomatoes": 18,
    "potatoes": 22
}

def get_item_price(item):
    if not item:
        return "Item not provided."
    print(f"Tool called for item {item}")
    price = grocery_prices.get(item.lower(), "unknown item price")
    return f"The price of a {item} is {price}."

def get_count_item(item):
    if not item:
        return "Item not provided"
    count = grocery_counts.get(item.lower(), "unknown item")
    return f"There are {count} of {item} in the stock."

# The structure that required to describe

price_function = {
    "name": "get_item_price",
    "description" : "Get the price of a item",
    "parameters": {
        "type": "object",
        "properties": {
            "item":{
                "type": "string",
                "description": "The item that the customer want the price"
            }
        },
        "required": ['item'],
        "additionalProperties": False
    }
}

count_function = {
    "name": "get_count_item",
    "description" : "Get available stock count of an item",
    "parameters": {
        "type": "object",
        "properties": {
            "item":{
                "type": "string",
                "description": "The item to check stock count"
            }
        },
        "required": ['item'],
        "additionalProperties": False
    }
}


tools = [
    {"type": "function", "function": price_function}, 
    {"type": "function", "function": count_function}
]


def handle_tool_call(message):
    """
    Converts assistant's tool calls into actual results.
    Returns a list of tool messages with role="tool".
    """
    tool_messages = []

    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "get_item_price":
            item = arguments.get("item")
            result = get_item_price(item)

        elif function_name == "get_count_item":
            item = arguments.get("item")
            result = get_count_item(item)

        else:
            result = "Unknown function call."

        tool_messages.append({
            "role": "tool",
            "content": result,
            "tool_call_id": tool_call.id
        })
    return tool_messages


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
    return (
        "You are a friendly grocery assistant. "
        "For general questions about items, health, nutrition, or usage, do NOT call any tools—just answer naturally. "
        "Always answer in short, clear sentences. "
        "Your store only carries main items like bread, eggs, milk, etc., and does NOT have subtypes or variations like white bread, brown bread, or large eggs. "
        "Only call tools for price or stock count questions, and always use tool outputs exactly; do not make up answers. "
        "Do not return JSON or tool calls unless the user specifically asks for them. "
        "Avoid providing prices or counts for items not listed in the tools."
    )


def clear_chat_histroy():
    st.session_state['chat_history'] = [{"role": "assistant", "content": "How can I help you?"}]


def chat(messages, temp, top_p, tools):
    """
    Handles user input, tool calls, and generates the assistant's natural response.

    Workflow:
    1. User sends a message
    2. Assistant may generate tool calls
    3. Tool calls are executed and appended as role="tool"
    4. Assistant reads tool outputs and generates final response
    5. Repeat if tool outputs trigger more tool calls (while loop)
    """
    openai = OpenAI(base_url="http://localhost:11434/v1", api_key="None")
    
    # Initial model call
    response = openai.chat.completions.create(
        model="llama3.2",
        messages=messages,
        temperature=temp,
        top_p=top_p,
        tools=tools,
        tool_choice="auto"
    )
    
    # Keep looping while there are tool calls to handle (chained tools)
    while response.choices[0].finish_reason == "tool_calls":
        assistant_message = response.choices[0].message

        # Append the assistant message that triggered the tool calls
        messages.append({
            "role": assistant_message.role,
            "content": assistant_message.content or "",
            "tool_calls": assistant_message.tool_calls
        })

        # Handle all tool calls in this message
        tool_responses = handle_tool_call(assistant_message)

        # Append tool outputs as "tool" messages only
        for tr in tool_responses:
            messages.append(tr)

        # Call the model again to let it generate the next assistant message naturally
        response = openai.chat.completions.create(
            model="llama3.2",
            messages=messages,
            temperature=temp,
            top_p=top_p,
            tools=tools,
            tool_choice="auto"
        )
    
    # After all tool calls are handled, return the final assistant message
    return response.choices[0].message.content


# -----------------------------
# Sessions
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = [{"role": "assistant", "content": "How can I help you?"}]
    st.session_state.chat_history.append({"role": "assistant", "content": system_message()})

for i , msg in enumerate (st.session_state.chat_history):
    if i == 1 or msg["role"] == "tool":
        continue
    if msg["role"] == "assistant" and (not msg.get("content")) and msg.get("tool_calls"):
        continue
    st.chat_message(msg["role"]).write(msg["content"])

if "llm3_status" not in st.session_state:
    st.session_state["llm3_status"] = "Not started"


if prompt := st.chat_input():
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.spinner("Thinking..."):
        response = chat(messages=st.session_state['chat_history'],temp=st.session_state["temperature"],
                         top_p=st.session_state["top_p"], tools=tools)
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
    st.session_state["temperature"] = st.sidebar.slider("temperature", 0.01, 1.0, 0.01, 0.01)
    st.session_state["top_p"] = st.sidebar.slider("top_p", 0.01, 1.0, 0.9, 0.01)
st.sidebar.button('Clear Chat', on_click=clear_chat_histroy, icon="🧹")
st.sidebar.text_area(label="data", value=st.session_state['chat_history'])