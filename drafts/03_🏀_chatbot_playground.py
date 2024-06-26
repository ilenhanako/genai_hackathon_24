# similar to https://platform.openai.com/playground?mode=chat&model=gpt-3.5-turbo-16k
import streamlit as st

from utils.llm import (
    DEFAULT_FREQUENCY_PENALTY,
    DEFAULT_MAX_TOKENS,
    DEFAULT_N_PAST_MESSAGES,
    DEFAULT_PRESENCE_PENALTY,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    CompletionStream,
)


def clear_messages():
    if "chatbot_playground_messages" in st.session_state:
        del st.session_state["chatbot_playground_messages"]


st.title("Chatbot Playground")

with st.sidebar:
    sys_message = st.text_area(
        "System message", value="You are a helpful assistant.", on_change=clear_messages
    )
    n_past_messages = st.slider(
        "Include past messages",
        value=DEFAULT_N_PAST_MESSAGES,
        min_value=0,
        max_value=20,
        step=2,
    )
    with st.expander("Parameters"):
        temperature = st.slider(
            "Temperature", value=DEFAULT_TEMPERATURE, min_value=0.0, max_value=2.0
        )
        max_tokens = st.slider(
            "Max response", value=DEFAULT_MAX_TOKENS, min_value=1, max_value=16384
        )
        top_p = st.slider("Top P", value=DEFAULT_TOP_P, min_value=0.0, max_value=1.0)
        frequency_penalty = st.slider(
            "Frequency Penalty",
            value=DEFAULT_FREQUENCY_PENALTY,
            min_value=0.0,
            max_value=2.0,
        )
        presence_penalty = st.slider(
            "Presence Penalty",
            value=DEFAULT_PRESENCE_PENALTY,
            min_value=0.0,
            max_value=2.0,
        )

if "chatbot_playground_messages" not in st.session_state:
    st.session_state.chatbot_playground_messages = [
        {"role": "system", "content": sys_message}
    ]
messages = st.session_state.chatbot_playground_messages  # alias as shorthand

for message in messages:
    if message["role"] != "system":
        st.chat_message(message["role"]).write(message["content"])

if user_input := st.chat_input():
    st.chat_message("user").write(user_input)
    messages.append({"role": "user", "content": user_input})

    stream = CompletionStream(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    with stream as response:
        stream.completion = str(st.chat_message("assistant").write_stream(response))
    messages.append({"role": "assistant", "content": stream.completion})

    while len(messages) > n_past_messages + 1:  # limit context window
        messages.pop(1)  # preserve system message at index 0
