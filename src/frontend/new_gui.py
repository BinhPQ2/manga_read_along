import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
import os
import subprocess

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

        # Run the pipeline script
        progress_text = "Generating video in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)

        # Execute the pipeline script with real-time logging
        print("Running pipeline script...")
        result = subprocess.Popen(
            ["python", "pipeline.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,  # Line-buffered output
            universal_newlines=True
        )

        # Track progress and display output in real-time
        percent_complete = 0
        generated_video_path = "output/output_final/video_Padding_True.mp4"
        
        while not os.path.exists(generated_video_path):
            # Read each line from stdout and update progress
            line = result.stdout.readline()
            if line:
                print(line.strip())  # Print the line from stdout

            # Update the progress bar
            time.sleep(1)  # Wait for 1 second between progress updates
            percent_complete += 10
            my_bar.progress(min(percent_complete, 100), text=progress_text)

            if percent_complete >= 100:  # Reset progress bar after each cycle
                percent_complete = 0

        # Wait for the process to complete and capture any remaining output
        stdout, stderr = result.communicate()
        print("Standard Output:", stdout)
        print("Standard Error:", stderr)

        # Clear the progress bar
        my_bar.empty()

        # Check if the video was generated successfully
        if result.returncode == 0 and os.path.exists(generated_video_path):
            st.session_state.video_url = generated_video_path
            st.session_state.progress_complete = True
            st.success("Video generated successfully!")
        else:
            st.session_state.video_url = "https://files.vuxlinh.com/demo.mp4"
            st.warning("An error occurred or the video file was not found. Displaying the default video.")
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