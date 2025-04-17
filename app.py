from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Streamlit Chat", page_icon="💬")
st.title("Chatbot")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False

if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0

if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
    
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False    
        
def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

if not st.session_state.setup_complete:
    st.subheader("Personal Information", divider="rainbow")
    
    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""
        

    st.session_state["name"] = st.text_input(label = "Name", max_chars = 40, value = st.session_state["name"], placeholder = "Enter your Name")

    st.session_state["experience"] = st.text_area(label = "Experience", value = st.session_state["experience"], height = None, max_chars=200, placeholder="Describe your experience")

    st.session_state["skills"] = st.text_area(label = "SKILLS", value = st.session_state["skills"], height = None, max_chars=200, placeholder="List your skills!")

    # st.write(f"**Your Name**: {st.session_state["name"]}")
    # st.write(f"**Your Experience**: {st.session_state["experience"]}")
    # st.write(f"**Your Skills**: {st.session_state["skills"]}")

    st.subheader("Company and Position", divider="rainbow")
    
    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if "position" not in st.session_state:
        st.session_state["position"] = "Data Scientists"
    if "company" not in st.session_state:
        st.session_state["company"] = "Amazon"

    col1, col2 = st.columns(2)

    with col1:
        st.session_state["level"] = st.radio(
            "Choose level",
            key="visibility",
            options=["Junior", "Mid-level", "Senior"]
        )

    with col2:
        st.session_state["position"] = st.selectbox(
            "Choose a position",
            ("Data Scientists", "Data Engineer", " ML Engineer", "AI Engineer", "BI Analyst")
        )

    st.session_state["company"] = st.selectbox(
        "Choose a company",
        ("Amazon", "Meta", "Udemy", "CloudWithUs", "Nestle", "LinkedIN", "ABT Limited")
    )
    st.write(f"**Your Information**: {st.session_state["level"]} - {st.session_state["position"]} at {st.session_state["company"]}")

if st.button("Start Interview", on_click = complete_setup):
    st.write("Setup completed. Starting the Interview...")

if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:
    st.info(
    """
    Start by Introducing yourself.
    """,
    icon = "👋"
    )
    client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "system",
            "content": f"You are an HR executive that interviews an interviewee called {st.session_state["name"]} "
            f"with expirience {st.session_state["experience"]} and skills {st.session_state["skills"]}. "
            f"You should interview him for the position {st.session_state["level"]} {st.session_state["position"]} "
            f"at the company {st.session_state["company"]}"}]
        

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.user_message_count <5:   
        if prompt := st.chat_input("Your answer", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model = st.session_state["openai_model"],
                        messages= [
                            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                        ],
                        stream = True,
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.user_message_count += 1
    
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback")

if st.session_state.feedback_shown:
    st.subheader("Feedback")
    
    conversation_history = "\n".join(f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages)
    
    feedback_client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])
    
    feedback_completion = feedback_client.chat.completions.create(
        model = "gpt-4o",
        messages = [
            {
                "role": "system", "content": """You are a helpful tool that provides feedback on an Interviews performance.
                Before the feedback give score between 1 to 10.
                Follow this format:
                Overall Score: //Your score
                Feedback: //Here you put your feedback
                Give only feedbacks. Don't ask any additional questions.
                """},
            {"role": "user", "content": f"This is the Interview you need to evaluate. Keep in mind that you are only a tool. You should't engage any conversation. {conversation_history}"}
        ]
    )

    st.write(feedback_completion.choices[0].message.content)

    if st.button("Restart Interview", type = "primary"):
        streamlit_js_eval(js_expressions = "parent.window.location.reload()")