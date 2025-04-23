import streamlit as st
st.set_page_config(page_title="Rinned's Chatbot", layout="centered")

import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Custom CSS for animations and UI elements
st.markdown("""
    <style>
        :root {
            --user-color: #4361ee;
            --assistant-color: #3a0ca3;
            --accent-color: #f72585;
            --bg-gradient: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        body {
            background: var(--bg-gradient);
            font-family: 'Segoe UI', system-ui, sans-serif;
        }
        
        @keyframes messageIn {
            0% { opacity: 0; transform: translateX(30px) scale(0.9); }
            100% { opacity: 1; transform: translateX(0) scale(1); }
        }
        
        @keyframes assistantIn {
            0% { opacity: 0; transform: translateX(-30px) scale(0.9); }
            100% { opacity: 1; transform: translateX(0) scale(1); }
        }
        
        .chat-message {
            animation: messageIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            margin: 12px 0;
            position: relative;
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            color: white;
        }
        
        .user-message {
            background: var(--user-color);
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }
        
        .assistant-message {
            background: var(--assistant-color);
            margin-right: auto;
            border-bottom-left-radius: 4px;
            animation-name: assistantIn;
        }
        
        .timestamp {
            font-size: 0.7em;
            color: rgba(255,255,255,0.7);
            margin-top: 4px;
            display: block;
        }
        
        .reaction-buttons {
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }
        
        .reaction-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            border-radius: 50%;
            width: 28px;
            height: 28px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .reaction-btn:hover {
            transform: scale(1.2);
            background: rgba(255,255,255,0.3);
        }
        
        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            margin: 16px 0;
            color: #555;
        }
        
        .typing-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--accent-color);
            animation: typingAnimation 1.4s infinite ease-in-out;
            box-shadow: 0 0 8px rgba(247, 37, 133, 0.4);
        }
        
        @keyframes typingAnimation {
            0%, 60%, 100% { transform: translateY(0); opacity: 0.6; }
            30% { transform: translateY(-8px); opacity: 1; }
        }
        
        /* New UI Elements */
        .chat-header {
            background: linear-gradient(90deg, var(--user-color), var(--assistant-color));
            color: white;
            padding: 16px;
            border-radius: 12px 12px 0 0;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .message-container {
            transition: all 0.3s;
        }
        
        .message-container:hover {
            transform: translateY(-2px);
        }
        
        /* New Animations */
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        
        .float-animation {
            animation: float 3s ease-in-out infinite;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-header"><h1 class="float-animation">✨ Rinned\'s Chatbot ✨</h1></div>', unsafe_allow_html=True)

# Ensure messages are initialized before usage
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi, how can I help you today?"}
    ]

# Ensure reactions are initialized before usage
if "reactions" not in st.session_state:
    st.session_state["reactions"] = {}

# Add buttons for clearing, exporting, saving, loading chat history, clearing reactions, and showing chat history
col1, col2, col3, col4, col5, col6 = st.columns(6)

def convert_messages_to_text(messages):
    lines = []
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        timestamp = msg.get("timestamp", "")
        content = msg["content"]
        lines.append(f"[{timestamp}] {role}: {content}")
    return "\n".join(lines)

def save_chat_history():
    chat_text = convert_messages_to_text(st.session_state["messages"])
    filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(chat_text)
    st.success(f"Chat history saved to {filename}")

def load_chat_history(uploaded_file):
    if uploaded_file is not None:
        content = uploaded_file.read().decode("utf-8")
        lines = content.splitlines()
        loaded_messages = []
        for line in lines:
            if line.startswith("[") and "]" in line:
                try:
                    timestamp_end = line.index("]")
                    timestamp = line[1:timestamp_end]
                    rest = line[timestamp_end+2:]
                    role_end = rest.index(":")
                    role = rest[:role_end].strip().lower()
                    content = rest[role_end+1:].strip()
                    if role == "user":
                        loaded_messages.append({"role": "user", "content": content, "timestamp": timestamp})
                    elif role == "assistant":
                        loaded_messages.append({"role": "assistant", "content": content, "timestamp": timestamp})
                except Exception:
                    continue
        if loaded_messages:
            st.session_state["messages"] = loaded_messages
            st.success("Chat history loaded successfully.")
        else:
            st.warning("No valid chat messages found in the file.")

with col1:
    if st.button("Clear Chat History"):
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hi, how can I help you today?"}
        ]
        st.session_state["reactions"] = {}
        try:
            st.experimental_rerun()
        except AttributeError:
            st.stop()

with col2:
    chat_text = convert_messages_to_text(st.session_state["messages"])
    st.download_button(
        label="Export Chat History",
        data=chat_text,
        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

with col3:
    if st.button("Save Chat History"):
        save_chat_history()

with col4:
    uploaded_file = st.file_uploader("Load Chat History", type=["txt"])
    if uploaded_file is not None:
        load_chat_history(uploaded_file)

with col5:
    if st.button("Clear All Reactions"):
        st.session_state["reactions"] = {}

with col6:
    show_history = st.checkbox("Show Chat History", value=True)

if show_history:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            # Add timestamp if it exists
            timestamp = msg.get("timestamp", datetime.now().strftime("%H:%M"))
            message_class = "user-message" if msg["role"] == "user" else "assistant-message"
            st.markdown(f'<div class="message-container"><div class="chat-message {message_class}">{msg["content"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="timestamp">{timestamp}</div>', unsafe_allow_html=True)
            
            # Add reaction buttons if this is an assistant message
            if msg["role"] == "assistant":
                # Display emoji reaction buttons
                reaction_emojis = ["👍", "👎", "❤️"]
                if str(i) not in st.session_state.reactions:
                    st.session_state.reactions[str(i)] = []
                reactions = st.session_state.reactions[str(i)]

                def add_reaction(msg_index, emoji):
                    if emoji not in st.session_state.reactions[msg_index]:
                        st.session_state.reactions[msg_index].append(emoji)

                cols = st.columns(len(reaction_emojis))
                for idx, emoji in enumerate(reaction_emojis):
                    if cols[idx].button(emoji, key=f"react_{i}_{emoji}"):
                        add_reaction(str(i), emoji)

                # Show current reactions
                if reactions:
                    st.markdown(f"""
                        <div class="reaction-buttons">
                            {' '.join([f'<button>{r}</button>' for r in reactions])}
                        </div>
                    """, unsafe_allow_html=True)

# Help section
st.markdown("---")
st.markdown("### Help & Instructions")
st.markdown("""
- Type your message in the input box and press Enter to chat with the assistant.
- Use the buttons above to clear, save, load, or export chat history.
- React to assistant messages using the emoji buttons below each message.
- Clear all reactions using the 'Clear All Reactions' button.
""")

prompt = st.chat_input("Type your message here:")

if prompt:
    # Add user message with timestamp
    user_msg = {"role": "user", "content": prompt, "timestamp": datetime.now().strftime("%H:%M")}
    st.session_state.messages.append(user_msg)
    
    with st.chat_message("user"):
        st.markdown(f'<div class="message-container"><div class="chat-message user-message">{prompt}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="timestamp">{user_msg["timestamp"]}</div>', unsafe_allow_html=True)

    # 4b. Make sure your Gemini API key is configured (from .env).
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        st.info("Please add your Gemini API key to a .env file as GEMINI_API_KEY.")
        st.stop()

    # 4c. Initialize the Gemini client with your API key.
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")  # Use a stable model name

    # 4d. Call the Gemini API to generate a response, formatting history.
    gemini_messages = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            gemini_messages.append({"role": "user", "parts": [msg["content"]]})
        elif msg["role"] == "assistant":
            gemini_messages.append({"role": "model", "parts": [msg["content"]]})

    try:
        # Show typing indicator
        typing_container = st.empty()
        with typing_container:
            st.markdown("""
                <div class="typing-indicator pulse-animation">
                    <span>Assistant is thinking</span>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(1)  # Simulate typing delay

        response = model.generate_content(contents=gemini_messages)
        typing_container.empty()  # Clear typing indicator

        # Extract the generated text from the response
        assistant_reply = response.text

        # Append the assistant's reply with timestamp
        assistant_msg = {
            "role": "assistant", 
            "content": assistant_reply,
            "timestamp": datetime.now().strftime("%H:%M")
        }
        st.session_state.messages.append(assistant_msg)
        
        with st.chat_message("assistant"):
            st.markdown(f'<div class="chat-message">{assistant_reply}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="timestamp">{assistant_msg["timestamp"]}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred while calling the Gemini API: {e}")
        st.stop()