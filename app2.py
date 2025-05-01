from openai import OpenAI
import streamlit as st
import time

# Page configuration
st.set_page_config(
    page_title="CotBot - Your AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS to enhance the UI
st.markdown("""
<style>
    .main {
        background-color: #f5f7fa;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-title {
        text-align: center;
        color: #1e3a8a;
        margin-bottom: 20px;
        font-size: 42px;
        font-weight: 700;
        padding: 20px 0;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTextInput>div>div>input {
        border-radius: 20px;
    }
    div.st-chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    div.st-chat-message[data-testid="stChatMessageContent"] {
        background-color: #f0f4f8;
    }
    div.st-chat-message.user div[data-testid="stChatMessageContent"] {
        background-color: #e3f2fd;
    }
    div.st-chat-message.assistant div[data-testid="stChatMessageContent"] {
        background-color: #e8f5e9;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 10px;
        font-size: 14px;
        color: #64748b;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Header with animation
st.markdown('<div class="chat-title">🤖 CotBot</div>', unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.markdown("## CotBot Settings")
    model = st.selectbox(
        "Select Model", 
        ["gpt-3.5-turbo", "gpt-4"], 
        index=0,
        help="Choose the OpenAI model to use for responses"
    )
    
    st.markdown("---")
    st.markdown("### About CotBot")
    st.markdown("""
    CotBot is your AI assistant powered by OpenAI.
    Ask anything and get instant, helpful responses!
    """)
    
    # Show loading animation example
    if st.button("Show Loading Animation"):
        with st.spinner("Loading..."):
            time.sleep(3)
        st.success("Loading complete!")
    
    st.markdown("---")
    if st.button("Clear Chat History", type="primary"):
        st.session_state.messages = []
        st.rerun()

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = model
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat container with custom styling
chat_container = st.container()

# Display chat messages
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Placeholder for assistant's response
    if "thinking" in st.session_state and st.session_state.thinking:
        with st.chat_message("assistant"):
            st.write("Thinking...")

# Chat input
prompt = st.chat_input("Ask me anything...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Set thinking state
    st.session_state.thinking = True
    st.rerun()

# Process response after rerun
if "thinking" in st.session_state and st.session_state.thinking:
    # Get the last message
    last_user_message = [msg for msg in st.session_state.messages if msg["role"] == "user"][-1]
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(last_user_message["content"])
        
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            # Generate the response
            try:
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
                
                # Display the response stream with a typing effect
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌")
                        time.sleep(0.01)
                
                # Display the final response
                response_placeholder.markdown(full_response)
                
                # Add assistant response to messages
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
            # Reset thinking state
            st.session_state.thinking = False

# Footer
st.markdown('<div class="footer">© 2025 CotBot - Your AI Assistant</div>', unsafe_allow_html=True)
