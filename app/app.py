import streamlit as st
import rag
import logging

# Configure logging to save logs to a file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/streamlit.log"),   # Save logs to a file named app.log
        # logging.StreamHandler()           # Output logs to console as well
    ]
)
logger = logging.getLogger(__name__)

def main():
    
    logger.debug("Starting the AI Audio Assistant streamlit app .....")
    
    st.title("AI Audio Assistant")

    # Course selection
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

    if st.button("Ask"):
        logger.debug(f"User asked: '{user_input}'")
        with st.spinner("Processing..."):
            logger.debug(f"Getting answer from assistant using {search_type} search")
            
            answer_data = rag.elastic_rag(user_input, playlist, search_type)
            
            st.success("Completed!")
            st.write(answer_data)

logger.debug("AI Audio Assistant app completed")


if __name__ == "__main__":
    logger.debug("AI Audio Assistant app started")
    main()
