import threading
from queue import Queue
import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
import os
import shutil
import subprocess
from config import RAW_IMAGE_PATH, CHARACTER_PATH, GENERATED_VIDEO_PATH, REENCODED_VIDEO_PATH

@st.cache_data()
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def save_uploaded_files(files, directory):
    for file in files:
        with open(os.path.join(directory, file.name), "wb") as f:
            f.write(file.getbuffer())

def call_api(url, colorize, panel_view, timeout, queue):
    """Call the API and put the response in a queue."""
    try:
        response = requests.post(
            url,
            json={
                "is_colorization": colorize,
                "is_panel_view": panel_view
            },
            timeout=timeout
        )
        response.raise_for_status()
        queue.put(response.json())
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        queue.put({"is_success": False})

st.set_page_config(page_title="Manga Video Generator Interface", page_icon=":movie_camera:", layout="wide")
st.title(":movie_camera: Manga Video Generator Interface")

with st.sidebar:
    lottie = load_lottieurl("https://assets6.lottiefiles.com/packages/lf20_cjnxwrkt.json")
    st_lottie(lottie)
    st.header("Team Info")
    with st.expander("", expanded=True):
        st.write("23C11018 - Phạm Quốc Bình")
        st.write("23C11054 - Nguyễn Khắc Toàn")
    st.header("Instructions")
    st.write("**Step 1**: Upload Raw Images. (Recommended format name: 01.jpg, 02.jpg, 03.jpg, ...)")
    st.write("**Step 2**: Upload Character Images with names. (Example: ruri_1.jpg, ukka_1.jpg...)")
    st.write("**Step 3**: Check the option box if needed.")
    st.write("**Step 4**: Click 'Generate Video' to generate the video.")

if os.path.exists(RAW_IMAGE_PATH):
    shutil.rmtree(RAW_IMAGE_PATH)
if os.path.exists(CHARACTER_PATH):
    shutil.rmtree(CHARACTER_PATH)
os.makedirs(RAW_IMAGE_PATH, exist_ok=True)
os.makedirs(CHARACTER_PATH, exist_ok=True)

st.header("Upload Chapter Pages")
chapter_files = st.file_uploader("Upload images for Chapter Pages", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
if not chapter_files:
    st.warning("⚠️ Please upload images for Chapter Pages.")

st.header("Upload Character Reference Images")
character_files = st.file_uploader("Upload images for Character Reference", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
if not character_files:
    st.warning("⚠️ Please upload images for Character Reference.")

colorize = st.checkbox("Colorization")
panel_view = st.checkbox("Panel View")

if "video_url" not in st.session_state:
    st.session_state.video_url = ""
if "progress_complete" not in st.session_state:
    st.session_state.progress_complete = False

if st.button("Generate Video", icon="🔥", use_container_width=True):
    st.session_state.video_url = ""
    st.session_state.progress_complete = False

    if chapter_files and character_files:
        save_uploaded_files(chapter_files, RAW_IMAGE_PATH)
        save_uploaded_files(character_files, CHARACTER_PATH)

        progress_text = "Generating video in progress. Please wait."
        my_bar = st.progress(0)
        progress = 0

        start_time = time.time()
        timeout_seconds = 600

        response_queue = Queue()

        api_thread = threading.Thread(target=call_api, args=("http://localhost:8000/generate-manga", colorize, panel_view, timeout_seconds, response_queue))
        api_thread.start()

        while (time.time() - start_time < timeout_seconds) and response_queue.empty():
            progress = (progress + 5) % 100
            my_bar.progress(progress, text=progress_text)
            time.sleep(1)

        if not response_queue.empty():
            data = response_queue.get()
        else:
            data = {"is_success": False}

        my_bar.empty()

        if data.get("is_success"):
            st.session_state.video_url = GENERATED_VIDEO_PATH
            st.session_state.progress_complete = True
            st.success("Video generated successfully!")
        else:
            st.session_state.video_url = ""
            st.warning("An error occurred or the video file was not found. Displaying the default video.")

    else:
        st.error("Please fill in all required fields before generating the video.")

st.header("Play Output Video")

if os.path.exists(REENCODED_VIDEO_PATH):
    st.session_state.video_url = REENCODED_VIDEO_PATH
    if os.path.isfile(st.session_state.video_url):
        with open(st.session_state.video_url, "rb") as video_file:
            video_bytes = video_file.read()
        st.video(video_bytes)
    else:
        st.write("Video file found but could not be read. Please check the file permissions or try regenerating.")
else:
    st.write("No video to display. Click 'Generate Video' to load the video.")