import threading
from queue import Queue
import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
import os
import tempfile
import shutil

@st.cache_data()
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def clear_folders():
    root_path = "/kaggle/working/"
    raw_image_path = os.path.join(root_path, "manga_read_along/input/raw")
    character_path = os.path.join(root_path, "manga_read_along/input/character")
    raw_image_rename_path = os.path.join(root_path, "output/renamed")
    colorized_path = os.path.join(root_path, "output/colorized")
    json_path = os.path.join(root_path, "output/json")
    transcript_path = os.path.join(root_path, "output/transcript")
    audio_path = os.path.join(root_path, "output/audio")
    final_output_path = os.path.join(root_path, "output/output_final")
    folders_to_delete = [raw_image_path, character_path, raw_image_rename_path, colorized_path, json_path]

    for folder in folders_to_delete:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            os.makedirs(folder)  # Re-create the empty folder

    # Reset session state for video URL and progress
    st.session_state.video_url = ""
    st.session_state.progress_complete = False
    st.success("Cleared all data and reset folders successfully.")

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

def call_api(url, colorize, timeout, queue):
    """Call the API and put the response in a queue."""
    try:
        response = requests.post(
            url,
            json={"is_colorization": colorize},
            timeout=timeout
        )
        response.raise_for_status()
        queue.put(response.json())  # Put the response in the queue
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        queue.put({"is_success": False})  # Put a failure response in the queue if there's an error

# Assume necessary imports, paths, and setup code are here
generated_video_path = "/kaggle/working/output/output_final/video_Padding_True.mp4"
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

        # Initialize progress bar and progress text
        progress_text = "Generating video in progress. Please wait."
        my_bar = st.progress(0)
        progress = 0  # Start progress

        # Start time tracking for timeout
        start_time = time.time()
        timeout_seconds = 600  # 10 minutes

        # Queue to retrieve the response from the thread
        response_queue = Queue()

        # Start API call in a separate thread
        api_thread = threading.Thread(target=call_api, args=("http://localhost:8000/generate-manga", colorize, timeout_seconds, response_queue))
        api_thread.start()

        # Run progress bar in increments while waiting for the API response
        while (time.time() - start_time < timeout_seconds) and response_queue.empty():
            # Update the progress bar in a loop
            progress = (progress + 5) % 100
            my_bar.progress(progress, text=progress_text)
            time.sleep(1)  # Adjust speed for smooth progress bar animation

        # Get the response from the queue if available
        if not response_queue.empty():
            data = response_queue.get()
        else:
            data = {"is_success": False}  # Timeout, set failure response

        # Clear the progress bar
        my_bar.empty()

        # Check if the video was generated successfully
        if data.get("is_success"):
            #generated_video_path = "/kaggle/working/output/output_final/video_Padding_True.mp4"
            st.session_state.video_url = generated_video_path
            st.session_state.progress_complete = True
            st.success("Video generated successfully!")
        else:
            # If generation fails or the file doesn't exist, set the default video URL
            st.session_state.video_url = "https://files.vuxlinh.com/demo.mp4"
            st.warning("An error occurred or the video file was not found. Displaying the default video.")

    else:
        st.error("Please fill in all required fields before generating the video.")

if right.button("Clear", icon="💣", use_container_width=True):
    clear_folders()
    st.session_state.video_url = ""
    st.session_state.progress_complete = False

st.header("Play Output Video")
if st.session_state.video_url:
    if st.session_state.video_url.startswith("http"):
        # For online video URLs, embed using HTML
        video_html = f"""
            <div style="width: 100%; height: auto;">
                <video width="100%" height="720" controls>
                    <source src="{st.session_state.video_url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
        """
        st.markdown(video_html, unsafe_allow_html=True)
    elif os.path.exists(generated_video_path):
        with open(generated_video_path, "rb") as video_file:
            video_bytes = video_file.read()
        st.video(video_bytes)
    else:
        # If video file is missing, notify the user
        st.write("Video file not found. Click 'Generate Video' to try again.")
else:
    st.write("No video to display. Click 'Generate Video' to load the video.")