import streamlit as st
import time
import uuid

from config import APP_LOGS_PATH
from config import setup_logging
from rag import get_answer
from db import save_conversation, save_feedback, get_recent_conversations, get_feedback_stats, init_db

logger = setup_logging(APP_LOGS_PATH)

def main():
    
    logger.info("Starting YouTube Browser streamlit app .....")
    
    # Session state initialization
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        logger.info(f"New conversation started with ID: {st.session_state.conversation_id}")
        
    if "count" not in st.session_state:
        st.session_state.count = 0
        logger.info("Feedback count initialized to zero.")
    
    st.title("YouTube Browser")

    # Select a YouTube playlist
    playlist = st.selectbox(
        "Select playlist from 'The Sound of AI' YouTube channel:",
        ["Audio Signal Processing for ML", "Audio Deep Learning with Python"],
    )
    logger.info(f"The following playlist has been selected: {playlist}")

    # Search type selection
    search_type = st.radio("Select the method of search:", ["Text", "Vector"])
    logger.info(f"The following method has been selected: {search_type}")

    # User input
    user_input = st.text_input("Write your question below:")

    if st.button("Send a question to AI"):
        if not user_input:
            st.error("Please enter a question before submitting.")
            logger.error("Please enter a question before submitting.")
            return
        
        # Generate a new conversation ID for next question
        st.session_state.conversation_id = str(uuid.uuid4())
        
        logger.info(f"User asked: '{user_input}'")
        with st.spinner("AI thinks ... AI thinks ..."):
            logger.info(f"Getting answer from YouTube Browser using {search_type} search")
            
            start_time = time.time()
            answer_data = get_answer(user_input, playlist, search_type)
            end_time = time.time()
            logger.info(f"Answer received in {end_time - start_time:.2f} seconds.")
            st.success("AI found the answer! Check it out!")
            st.write(answer_data["answer"])
            
            # Display monitoring information
            st.write(f"Response time: {answer_data['response_time']:.2f} seconds")
            st.write(f"Relevance: {answer_data['relevance']}")
            st.write(f"Total tokens: {answer_data['total_tokens']}")
            st.write(f"Total evaluation tokens: {answer_data['eval_total_tokens']}")
            if answer_data["openai_cost"] > 0:
                st.write(f"OpenAI cost: ${answer_data['openai_cost']:.4f}")

            # Save conversation to database
            save_conversation(st.session_state.conversation_id, user_input, answer_data, playlist)
            
            
    # Feedback buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Excellent! Awesome!"):
            st.session_state.count += 1
            logger.info(f"Positive feedback received. New count: {st.session_state.count}")
            save_feedback(st.session_state.conversation_id, 1)
            logger.info("Positive feedback saved to database")
            # Generate a new conversation ID for next question
            st.session_state.conversation_id = str(uuid.uuid4())
    with col2:
        if st.button("👎 AI needs to get smarter!"):
            st.session_state.count -= 1
            logger.info(f"Negative feedback received. New count: {st.session_state.count}")
            save_feedback(st.session_state.conversation_id, -1)
            logger.info("Negative feedback saved to database")
            # Generate a new conversation ID for next question
            st.session_state.conversation_id = str(uuid.uuid4())

    st.write(f"Current count: {st.session_state.count}")
    
    # Display feedback stats
    feedback_stats = get_feedback_stats()
    st.subheader("Feedback Statistics")
    st.write(f"Thumbs up: {feedback_stats['thumbs_up']}")
    st.write(f"Thumbs down: {feedback_stats['thumbs_down']}")

    # Display recent conversations
    st.subheader("Recent Conversations")
    relevance_filter = st.selectbox(
        "Filter by relevance:", ["All", "RELEVANT", "PARTICULARLY_RELEVANT", "NOT_RELEVANT"]
    )
    recent_conversations = get_recent_conversations(
        limit=5, relevance=relevance_filter if relevance_filter != "All" else None
    )
    for conv in recent_conversations:
        st.write(f"Q: {conv['question']}")
        st.write(f"A: {conv['answer']}")
        st.write(f"Relevance: {conv['relevance']}")
        st.write("---")

if __name__ == "__main__":
    # logger.info("DB initialization stage started ... ")
    # init_db()
    # logger.info("DB initialization stage was completed.")
    logger.info("YouTube Browser app started")
    main()
    logger.info("YouTube Browser app completed")