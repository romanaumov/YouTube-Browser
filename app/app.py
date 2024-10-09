import streamlit as st
import logging
import time
import uuid
from rag import get_answer
from db import save_conversation, save_feedback, get_recent_conversations, get_feedback_stats, init_db

# Configure logging to save logs to a file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/streamlit.log"),   # Save logs to a file named app.log
        # logging.StreamHandler()           # Output logs to console as well
    ]
)

def main():
    
    logger.debug("Starting YouTube Browser streamlit app .....")
    
    # Session state initialization
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        logger.debug(f"New conversation started with ID: {st.session_state.conversation_id}")
        
    if "count" not in st.session_state:
        st.session_state.count = 0
        logger.debug("Feedback count initialized to zero.")
    
    st.title("YouTube Browser")

    # Select a YouTube playlist
    playlist = st.selectbox(
        "Select playlist from 'The Sound of AI' YouTube channel:",
        ["Audio Signal Processing for ML", "Audio Deep Learning with Python"],
    )
    logger.debug(f"The following playlist has been selected: {playlist}")

    # Search type selection
    search_type = st.radio("Select the method of search:", ["Text", "Vector"])
    logger.debug(f"The following method has been selected: {search_type}")

    # User input
    user_input = st.text_input("Write your question below:")

    if st.button("Send a question to AI"):
        if not user_input:
            st.error("Please enter a question before submitting.")
            return
        
        # Generate a new conversation ID for next question
        st.session_state.conversation_id = str(uuid.uuid4())
        
        logger.debug(f"User asked: '{user_input}'")
        with st.spinner("AI thinks ... AI thinks ..."):
            logger.debug(f"Getting answer from YouTube Browser using {search_type} search")
            
            start_time = time.time()
            answer_data = get_answer(user_input, playlist, search_type)
            end_time = time.time()
            logger.debug(f"Answer received in {end_time - start_time:.2f} seconds.")
            st.success("AI found the answer! Check it out!")
            st.write(answer_data["answer"])
            
            # Display monitoring information
            st.write(f"Response time: {answer_data['response_time']:.2f} seconds")
            if answer_data["openai_cost"] > 0:
                st.write(f"OpenAI cost: ${answer_data['openai_cost']:.4f}")

            # Save conversation to database
            logger.debug("Saving conversation to database")
            save_conversation(
                st.session_state.conversation_id, user_input, answer_data, playlist
            )
            logger.debug("Conversation saved successfully")
            
            
    # Feedback buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Excellent! Awesome!"):
            st.session_state.count += 1
            logger.debug(f"Positive feedback received. New count: {st.session_state.count}")
            save_feedback(st.session_state.conversation_id, 1)
            logger.debug("Positive feedback saved to database")
            # Generate a new conversation ID for next question
            st.session_state.conversation_id = str(uuid.uuid4())
    with col2:
        if st.button("👎 AI needs to get smarter!"):
            st.session_state.count -= 1
            logger.debug(f"Negative feedback received. New count: {st.session_state.count}")
            save_feedback(st.session_state.conversation_id, -1)
            logger.debug("Negative feedback saved to database")
            # Generate a new conversation ID for next question
            st.session_state.conversation_id = str(uuid.uuid4())

    st.write(f"Current count: {st.session_state.count}")

    # Display recent conversations
    st.subheader("Recent Conversations")
    recent_conversations = get_recent_conversations(limit=5)
    
    for conv in recent_conversations:
        st.write(f"Q: {conv['question']}")
        st.write(f"A: {conv['answer']}")
        st.write("----------------------")

    # Display feedback stats
    feedback_stats = get_feedback_stats()
    st.subheader("Feedback Statistics")
    st.write(f"Thumbs up: {feedback_stats['thumbs_up']}")
    st.write(f"Thumbs down: {feedback_stats['thumbs_down']}")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.debug("YouTube Browser app started")
    init_db()
    main()
    logger.debug("YouTube Browser app completed")