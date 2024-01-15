from openai import OpenAI
import streamlit as st
import time

ASSISTANT_ID = "asst_QQ0B31JvOlT982sdY4xEgmXP"

with st.sidebar:
    st.image('8min_icon.png', caption='8 minutes', width=128)
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    st.text('Citation')
    sidebar_text = st.empty()

st.title("💬 8min Chatbot")
st.caption("🚀 A streamlit chatbot to talk about content in podcast <8 minutes>. Only season 1 contents supported.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "不保证成功，不一定有用，知识只是点亮世界的灵光。我是梁文道。"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)

    if "thread" not in st.session_state:
        st.session_state.thread = client.beta.threads.create()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    message = client.beta.threads.messages.create(
        thread_id=st.session_state.thread.id,
        role="user",
        content=prompt
    )

    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread.id,
        assistant_id=ASSISTANT_ID
    )

    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=st.session_state.thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            print("Run failed:", run_status.last_error)
            break
        time.sleep(2)  # wait for 2 seconds before checking again

    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread.id
    )

    number_of_messages = len(messages.data)

    for message in messages.data:
        role = message.role  
        for content in message.content:
            if content.type == 'text' and role == 'assistant':
                response = content.text.value 
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.chat_message("assistant").write(response)

                all_citation = ""
                for annotation in content.text.annotations:
                    all_citation += f"<span style='color: grey;font-size: 10;'>{annotation.text}\n{annotation.file_citation.quote}</span><br>"
                sidebar_text.markdown(all_citation, unsafe_allow_html=True)
                break
        break

