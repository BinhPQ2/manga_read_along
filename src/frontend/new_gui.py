import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
import os

@st.cache_data()
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Set up Streamlit UI
st.set_page_config(page_title="Manga Video Generator Interface", page_icon=":movie_camera:", layout="wide")
st.title(":movie_camera: Manga Video Generator Interface")

# Sidebar setup
with st.sidebar:
    lottie = load_lottieurl("https://assets6.lottiefiles.com/packages/lf20_cjnxwrkt.json")
    st_lottie(lottie)
    st.button("Upgrade to Plus", icon="🗝️", use_container_width=True)
    st.header("Team Info")
    with st.expander("", expanded=True):
        st.write("23C11018 - Phạm Quốc Bình")
        st.write("23C11054 - Nguyễn Khắc Toàn")
        st.write("23C15030 - Nguyễn Vũ Linh")
        st.write("23C15037 - Bùi Trọng Quý")
    st.header("Instructions")
    st.write("**Step 1**: Upload Chapter Pages and Character Reference Images.")
    st.write("**Step 2**: Enter Character Names (comma separated).")
    st.write("**Step 3**: Check the Colorization checkbox if needed.")
    st.write("**Step 4**: Click 'Generate Video' to generate the video.")
    st.write("**Step 5**: Click 'Clear' to clear all input fields.")

# Ensure directories exist
raw_image_path = "input/raw"
character_path = "input/character"
os.makedirs(raw_image_path, exist_ok=True)
os.makedirs(character_path, exist_ok=True)

# File upload for Chapter Pages
st.header("Upload Chapter Pages")
chapter_files = st.file_uploader("Upload images for Chapter Pages", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
if not chapter_files:
    st.warning("⚠️ Please upload images for Chapter Pages.")

# File upload for Character Reference Images
st.header("Upload Character Reference Images")
character_files = st.file_uploader("Upload images for Character Reference", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
if not character_files:
    st.warning("⚠️ Please upload images for Character Reference.")

# Character names input
st.header("Character Names")
character_names = st.text_input("Enter Character Names (comma separated)", placeholder="Luffy,Hank,Nami")

# Colorization option
colorize = st.checkbox("Colorization")

# Function to save uploaded files
def save_uploaded_files(files, directory):
    for file in files:
        with open(os.path.join(directory, file.name), "wb") as f:
            f.write(file.getbuffer())

# Initialize session state
if "video_url" not in st.session_state:
    st.session_state.video_url = ""
if "progress_complete" not in st.session_state:
    st.session_state.progress_complete = False

left, right = st.columns(2)

def wait_for_api_response(api_url, colorize, timeout=600):
    """Send request to the API and wait for response within the specified timeout."""
    start_time = time.time()
    while True:
        try:
            response = requests.post(api_url, json={"is_colorization": colorize})
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException:
            # Check for timeout (10 minutes)
            if time.time() - start_time > timeout:
                return None  # Return None if API request times out
            time.sleep(5)  # Retry every 5 seconds

# Assume necessary imports, paths, and setup code are here

if left.button("Generate Video", icon="🔥", use_container_width=True):
    if chapter_files and character_files:
        st.session_state.video_url = ""
        st.session_state.progress_complete = False

        # Save the uploaded files to respective directories
        save_uploaded_files(chapter_files, raw_image_path)
        save_uploaded_files(character_files, character_path)

        # Save character names
        with open(os.path.join(character_path, "character_names.txt"), "w") as f:
            f.write(character_names)

        # Initialize progress bar and text placeholder
        progress_text = "Generating video in progress. Please wait."
        my_bar = st.progress(0)
        progress_loop_active = True  # To control the progress loop

        def run_progress_bar():
            """Simulate a continuous progress bar loop until stopped."""
            progress = 0
            while progress_loop_active:
                progress = (progress + 10) % 100
                my_bar.progress(progress)
                time.sleep(0.1)  # Adjust speed as necessary

        # Start progress bar loop in a separate thread
        import threading
        progress_thread = threading.Thread(target=run_progress_bar)
        progress_thread.start()

        # Call the API and wait for the response, with a 10-minute timeout
        data = wait_for_api_response("http://localhost:8000/generate-manga", colorize, timeout=600)

        # Stop the progress bar loop
        progress_loop_active = False
        progress_thread.join()  # Ensure the progress thread stops

        # Clear the progress bar
        my_bar.empty()

        # Check the API response and display the appropriate video
        generated_video_path = "output/output_final/video_Padding_True.mp4"
        if data and data.get("is_success") and os.path.exists(generated_video_path):
            st.session_state.video_url = generated_video_path
            st.session_state.progress_complete = True
            st.success("Video generated successfully!")
        elif data is None:
            st.error("The request timed out after 10 minutes. Please try again later.")
        else:
            st.session_state.video_url = "https://files.vuxlinh.com/demo.mp4"
            st.warning("An error occurred during video generation. Displaying the default video.")

    else:
        st.error("Please fill in all required fields before generating the video.")

if right.button("Clear", icon="💣", use_container_width=True):
    st.session_state.video_url = ""
    st.session_state.progress_complete = False

st.header("Play Output Video")
if st.session_state.video_url:
    video_html = f"""
        <div style="width: 100%; height: auto;">
            <video width="100%" height="720" controls>
                <source src="{st.session_state.video_url}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    """
    st.markdown(video_html, unsafe_allow_html=True)
else:
    st.write("No video to display. Click 'Generate Video' to load the video.")