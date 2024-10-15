import streamlit as st
import time
import uuid

from config import APP_LOGS_PATH
from config import setup_logging
from rag import get_answer
from db import save_conversation, save_feedback, get_recent_conversations, get_feedback_stats

logger = setup_logging(APP_LOGS_PATH)

def main():
    
    logger.info("Starting YouTube Browser streamlit app .....")
    
    # Set the page configuration
    st.set_page_config(page_title="YouTube Browser", page_icon="🔍", layout="centered")
    
    # Session state initialization
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        logger.info(f"New conversation started with ID: {st.session_state.conversation_id}")
        
    if "count" not in st.session_state:
        st.session_state.count = 0
        logger.info("Feedback count initialized to zero.")
    
    st.markdown("""
        <style>
            .main {
                max-width: 85%;  /* Keeps the content wider but centered */
                margin: 0 auto;
                background-color: #1a1a1a;  /* Dark background for professional feel */
                color: #f0f2f6;  /* Light text for readability */
            }
            .title {
                font-size: 2.5rem;
                font-weight: bold;
                color: #f0f2f6;  /* White text for title to pop */
                text-align: center;  /* Center-align title */
            }
            .subheader {
                font-size: 1.5rem;
                font-weight: bold;
                color: #ff9900;  /* Orange for a bold subheader */
                text-align: center;  /* Center-align title */
            }
            .stButton>button {
                background-color: #0D4C92;  /* Blue button background for professional look */
                color: white;  /* White text on button for contrast */
                border-radius: 5px;  /* Rounded corners for better design */
                padding: 10px 20px;  /* Add padding for a more clickable feel */
                font-size: 1rem;
                transition: background-color 0.3s ease;  /* Smooth hover transition */
            }
            .stButton>button:hover {
                background-color: #0b3a6f;  /* Darker blue on hover */
            }
        </style>
    """, unsafe_allow_html=True)
    
    # UI sidebar
    with st.sidebar:
        
        st.write("")
        st.write("")
        
        # Select a YouTube channel
        yt_channel = st.selectbox("Select YouTube channel:", ["The Sound of AI"])
        
        # Add an empty line for spacing
        st.write("")
        st.write("")
        st.write("")
        
        # Select a YouTube playlist
        playlist = st.selectbox(
            f"Select playlist from {yt_channel} YouTube channel:",
            ["Audio Signal Processing for ML", "Audio Deep Learning with Python"],
        )
        logger.info(f"The following playlist has been selected: {playlist}")
        
        # search_type = st.radio("Choose the method of search:", ["Text", "Vector"])
        search_type = "Text"
        # openai_key = st.text_input(label="Your OpenAI API key", help="If you have your own API key, please use it. Your API key will not be stored anywhere.")
        
        # Add an empty line for spacing
        st.write("")
        st.write("")
        
        # Display feedback stats
        st.subheader("Feedback statistics")
        feedback_stats = get_feedback_stats()
        st.write(f"👍 - {feedback_stats['thumbs_up']} reviews.")
        st.write(f"👎 - {feedback_stats['thumbs_down']} reviews.")
        
        st.write("")
        st.write("")
        
        st.subheader("YouTube Browser statistics")
        st.markdown('''
                    [Dashboard](http://localhost:3000/d/adc5a433-4aa1-4226-b590-6a4b98529ae0/response-time?orgId=1&from=1728709200000&to=1729000800000)
                    ''', unsafe_allow_html=True)

        st.write("")
        st.write("")

        st.markdown('''
                    The dataset was created by transcribing audio tracks from the selected channel.
                    The transcription of the audio files was processed by [Amazon Transcribe](https://aws.amazon.com/pm/transcribe/) service.
                    ''', unsafe_allow_html=True)
        st.markdown('''GitHub repository of this project: [GitHub](https://github.com/romanaumov/YouTube-Browser)''', unsafe_allow_html=True)
        st.markdown('''
                    The app was created by [Roman Naumov](https://www.linkedin.com/in/RomaNaumov) 
                    as a part of [LLM-Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp) course.
                    ''', unsafe_allow_html=True)
        st.markdown('''@YouTube Browser, 2024''', unsafe_allow_html=True)
    
    
    # Title of the app
    st.markdown("<h1 class='title'>🔍 YouTube Browser</h1>", unsafe_allow_html=True)

    # Add an empty line for spacing
    st.write("")

    # Introduction text
    st.markdown("<h3 class='subheader'>Welcome to YouTube Browser's intelligent search engine, <br> powered by LLM!</h3>", unsafe_allow_html=True)
    
    st.markdown('''
                This amazing app will help you find the information you need from YouTube video content.
                **You don't need to waste time watching videos!**
                
                Just select a YouTube channel and playlist, ask a question and get an answer on a specific topic from the content of the selected YouTube channel.
                
                Finally, the answer can be **verified by watching a short video fragment** that directly relates to the question. 
                ''')

    logger.info(f"The following method has been selected: {search_type}")

    # Add an empty line for spacing
    st.write("")
    
    # User input
    user_input = st.text_input("Write your question:")

    if st.button("Send a question to AI"):
        if not user_input:
            st.error("Please enter a question before submitting.")
            logger.error("Please enter a question before submitting.")
            return
        
        # Generate a new conversation ID for next question
        st.session_state.conversation_id = str(uuid.uuid4())
        
        logger.info(f"User asked: '{user_input}'")
        try:
            with st.spinner("AI generating awesome answer for you...⏳"):
                logger.info(f"Getting answer from YouTube Browser using {search_type} search")
                
                start_time = time.time()
                answer_data = get_answer(user_input, playlist, search_type)
                end_time = time.time()
                logger.info(f"Answer received in {end_time - start_time:.2f} seconds.")
                st.success("AI found the answer! Check it out!")
                st.write(answer_data["answer"])

                # Save conversation to database
                save_conversation(st.session_state.conversation_id, user_input, answer_data, playlist)
                
        except Exception as e:
            st.error("Sorry, there was an issue generating the answer. Please try again later.")
            logger.error(f"Error in AI response: {e}")
                
    # Add an empty line for spacing
    st.write("")
    st.write("")
        
    # logger.info(f"question_answered_flag: {question_answered}")
    # if question_answered:
    # Display recent conversations
    st.subheader("Your feedback")

    # Feedback buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Excellent! Awesome!"):
            st.session_state.count += 1
            logger.info(f"Positive feedback received. New count: {st.session_state.count}")
            save_feedback(st.session_state.conversation_id, 1)
            logger.info("Positive feedback saved to database")
    with col2:
        if st.button("👎 AI needs to get smarter!"):
            st.session_state.count -= 1
            logger.info(f"Negative feedback received. New count: {st.session_state.count}")
            save_feedback(st.session_state.conversation_id, -1)
            logger.info("Negative feedback saved to database")
    
    # Display recent conversations
    st.subheader("Recent Conversations")
    relevance_filter = st.selectbox(
        "Filter by relevance (5 last conversations):", [" ", "All", "RELEVANT", "PARTICULARLY_RELEVANT", "NOT_RELEVANT"]
    )
    
    if relevance_filter != " ":
        recent_conversations = get_recent_conversations(
            limit=5, relevance=relevance_filter if relevance_filter != "All" else None
        )
        for conv in recent_conversations:
            st.write(f"Q: {conv['question']}")
            st.write(f"A: {conv['answer']}")
            st.write(f"Relevance: {conv['relevance']}")
            st.write("---")

if __name__ == "__main__":
    logger.info("YouTube Browser app started")
    main()
    logger.info("YouTube Browser app completed")