import google.generativeai as genai
import streamlit as st
import time

# Page configuration
st.set_page_config(
    page_title="CotBot - Your AI Assistant",
    page_icon="💬",
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
st.markdown('<div class="chat-title">💬 CotBot</div>', unsafe_allow_html=True)

# Configure Gemini API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Sidebar for settings
with st.sidebar:
    st.markdown("## CotBot Settings")
    model = st.selectbox(
        "Select Model", 
        ["gemini-pro", "gemini-1.5-pro"], 
        index=0,
        help="Choose the Google Gemini model to use for responses"
    )
    
    temperature = st.slider(
        "Temperature", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.7, 
        step=0.1,
        help="Higher values make output more creative, lower values make it more deterministic"
    )
    
    st.markdown("---")
    st.markdown("### About CotBot")
    st.markdown("""
    CotBot is your AI assistant powered by Google Gemini.
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
        st.session_state.gemini_history = []
        st.rerun()

# Initialize session state
if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = model
if "messages" not in st.session_state:
    st.session_state.messages = []
if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = []

# Initialize Gemini model
if "model_instance" not in st.session_state or st.session_state.gemini_model != model:
    st.session_state.gemini_model = model
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 2048,
    }
    
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ]
    
    st.session_state.model_instance = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    
    # Initialize chat session
    st.session_state.chat = st.session_state.model_instance.start_chat(history=st.session_state.gemini_history)

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
                with st.spinner("Gemini is thinking..."):
                    # Send the message to Gemini
                    response = st.session_state.chat.send_message(
                        content=last_user_message["content"],
                        stream=True
                    )
                    
                    # Stream the response
                    for chunk in response:
                        if chunk.text:
                            full_response += chunk.text
                            response_placeholder.markdown(full_response + "▌")
                            time.sleep(0.01)
                    
                    # Display the final response
                    response_placeholder.markdown(full_response)
                    
                    # Add assistant response to messages
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    # Update Gemini history for context maintenance
                    st.session_state.gemini_history = [
                        {"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]}
                        for msg in st.session_state.messages
                    ]
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
            # Reset thinking state
            st.session_state.thinking = False

# Footer
st.markdown('<div class="footer">© 2025 CotBot - Powered by Google Gemini</div>', unsafe_allow_html=True)
