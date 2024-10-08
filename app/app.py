import streamlit as st
import rag
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    
    print("Starting the AI Audio Assistant streamlit app .....")
    st.title("AI Audio Assistant")

    # Course selection
    playlist = st.selectbox(
        "Select playlist from 'The Sound of AI' YouTube channel:",
        ["Audio Signal Processing for ML", "Audio Deep Learning with Python"],
    )
    print(f"The following playlist has been selected: {playlist}")

    # Search type selection
    search_type = st.radio("Select the method of search:", ["Text", "Vector"])
    print(f"The following method has been selected: {search_type}")

    # User input
    user_input = st.text_input("Write your question below:")

    if st.button("Ask"):
        print(f"User asked: '{user_input}'")
        with st.spinner("Processing..."):
            print(f"Getting answer from assistant using {search_type} search")
            
            answer_data = rag.elastic_rag(user_input, playlist, search_type)
            
            st.success("Completed!")
            st.write(answer_data)

print("AI Audio Assistant app completed")


if __name__ == "__main__":
    print("AI Audio Assistant app started")
    main()
