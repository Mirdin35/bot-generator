import streamlit as st
import requests
from decouple import config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# URL for backend API
BACKEND_URL = config("BACKEND_URL")

def process_voice_clone(uploaded_files, bot_name):
    """Send MP3 files to the FastAPI backend for voice cloning."""
    if not uploaded_files:
        st.error("❌ No files uploaded.")
        logger.warning("No files uploaded for voice cloning.")
        return None

    # Prepare files for request
    files = [("files", (file.name, file.getvalue(), "audio/mpeg")) for file in uploaded_files]
    data = {"bot_name": bot_name}

    try:
        logger.info("Sending voice clone request to backend.")
        response = requests.post(f"{BACKEND_URL}/process_voice_clone", files=files, data=data, timeout=30)
        response.raise_for_status()
        voice_data = response.json()
        voice_id = voice_data.get("voice_id")

        if voice_id:
            st.success(f"✅ Voice cloned successfully! Voice ID: {voice_id}")
            return voice_id
        else:
            st.error("❌ Voice ID not found in response.")
            st.json(voice_data)
            logger.error(f"Voice cloning response error: {voice_data}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error communicating with backend: {e}")
        logger.error(f"RequestException during voice cloning: {e}")
        return None

def main():
    """Main function of the Streamlit application."""
    st.title("Bot Generator")
    st.write("Fill in the form to create a new bot")

    # Initialize session state variables
    if "vector_store_processed" not in st.session_state:
        st.session_state.vector_store_processed = False
    if "vector_store_id" not in st.session_state:
        st.session_state.vector_store_id = None
    if "voice_clone_processed" not in st.session_state:
        st.session_state.voice_clone_processed = False
    if "voice_id" not in st.session_state:
        st.session_state.voice_id = None

    # Basic bot information
    bot_token = st.text_input("Bot Token *")
    bot_name = st.text_input("Bot Name *")
    bot_description = st.text_area("Bot Description", value='')
    start_message = st.text_area("Start Message", value='')
    help_message = st.text_area("Help Message", value='')
    system_prompt = st.text_area("System Prompt *", value='')

    # Knowledge base files section
    st.write("### Upload knowledge base files (Optional)")
    uploaded_files_vs = st.file_uploader(
        "Upload knowledge base files",
        accept_multiple_files=True,
        key="knowledge_base_uploader",
    )

    # Process knowledge base files if uploaded and not already processed
    if uploaded_files_vs and bot_name and not st.session_state.vector_store_processed:
        if st.button("Process Knowledge Base Files"):
            logger.info("Processing knowledge base files for bot: %s", bot_name)
            files = [("files", (f.name, f.getvalue())) for f in uploaded_files_vs]
            data = {"bot_name": bot_name}
            try:
                response = requests.post(
                    f"{BACKEND_URL}/process_knowledge_base",
                    files=files,
                    data=data,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                vector_store_id = data.get("vector_store_id")
                if vector_store_id:
                    st.session_state.vector_store_id = vector_store_id
                    logger.info("Knowledge base processed successfully: %s", vector_store_id)
                    st.success("✅ Knowledge base processed successfully!")
                else:
                    st.warning("⚠️ No files processed. Vector store will be empty.")
                st.session_state.vector_store_processed = True
            except requests.exceptions.RequestException as e:
                logger.error("Error processing knowledge base: %s", e)
                st.error(f"❌ Error processing knowledge base: {e}")

    # Ensure vector_store_id is explicitly None if no files are uploaded
    if not uploaded_files_vs:
        st.session_state.vector_store_id = None

    # Voice Cloning section
        # Voice Cloning section
    st.write("### Voice Cloning with 11labs *")
    uploaded_files_voice_clone = st.file_uploader(
        "Upload voice samples (MP3 or OGG)", type=["mp3", "ogg"], accept_multiple_files=True
    )

    if uploaded_files_voice_clone:
        if st.button("Process Voice Clone"):
            if bot_name:
                logger.info("Processing voice clone for bot: %s", bot_name)
                voice_id = process_voice_clone(uploaded_files_voice_clone, bot_name)
                if voice_id:
                    st.session_state.voice_id = voice_id
                    logger.info("Voice cloned successfully: %s", voice_id)
                else:
                    logger.error("Failed to process voice clone for bot: %s", bot_name)
                    st.error("❌ Failed to process voice clone.")
            else:
                logger.warning("Bot name is missing for voice cloning")
                st.error("❌ Please enter a bot name.")

    # Get IDs from session state
    vector_store_id = st.session_state.get('vector_store_id')
    voice_id = st.session_state.get('voice_id')

    # Submit button (create bot)
    if st.button("Submit"):
        if not all([bot_token, bot_name, system_prompt]):
            logger.warning("Missing required fields: Bot Token or Bot Name or System Prompt")
            st.error("⚠️ Please fill in all required fields! (*)")
            st.stop()

        if not voice_id:
            logger.warning("Voice ID missing, user needs to upload voice samples")
            st.error("⚠️ Please upload voice samples for cloning!")
            st.stop()

        with st.spinner("Creating your bot... This may take a moment..."):
            payload = {
                "bot_token": bot_token,
                "bot_name": bot_name,
                "bot_description": bot_description,
                "start_message": start_message,
                "help_message": help_message,
                "system_prompt": system_prompt,
                "vector_store_id": vector_store_id,
                "voice_id": voice_id,
            }
            logger.info("Sending bot creation request for: %s", bot_name)
            try:
                response = requests.post(
                    f"{BACKEND_URL}/create_bot",
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("success"):
                    logger.info("Bot created successfully: %s", bot_name)
                    st.success(f"✅ Bot created successfully!")
                    if "warning" in data:
                        logger.warning("Webhook setup warning: %s", data['warning'])
                else:
                    error_msg = data.get("error", "Unknown error")
                    logger.error("Failed to create bot: %s", error_msg)
                    st.error(f"❌ Failed to create bot: {error_msg}")
            except requests.exceptions.Timeout:
                logger.warning("Bot creation request timed out")
                st.warning("⚠️ Request timed out, but your bot might still have been created.")
            except requests.exceptions.RequestException as e:
                logger.error("Error creating bot: %s", e)
                st.error(f"⚠️ Error creating bot: {e}")

if __name__ == "__main__":
    main()